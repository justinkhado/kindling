import functools

from flask import (
    Blueprint, flash, redirect, render_template, session, request, url_for
)
from app.auth import login_required
from app.db import get_db

bp = Blueprint('books', __name__)


def has_profile(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        profile = get_db().execute(
            'SELECT * FROM books WHERE user_id = ?', (session.get('user_id'),)
        ).fetchone()

        if profile is None:
            return redirect(url_for('books.edit_profile'))

        return view(**kwargs)

    return wrapped_view


def get_new_book(user_id):
    db = get_db()

    books = db.execute(
        'SELECT id, title, desc'
        ' FROM books'
        ' LEFT JOIN seen_books'
        '  ON books.id = seen_books.book_id'
        ' WHERE books.user_id != ? AND'
        '  books.id NOT IN ('
        '   SELECT book_id FROM seen_books WHERE user_id = ?)',
        (user_id, user_id)
    ).fetchall()

    profile = None
    if len(books) != 0:
        profile = books[0]

    genres = []
    book = {'title': '', 'desc': 'No books left'}
    if profile is not None:
        genre_ids = db.execute(
            'SELECT genre_id FROM book_genres'
            ' WHERE book_id = ?', (profile['id'],)
        ).fetchall()

        for genre_id in genre_ids:
            genres.append(db.execute(
                'SELECT genre FROM genres'
                ' WHERE id = ?', (genre_id[0],)
            ).fetchone()[0])

        book = {
            'id': profile['id'],
            'title': profile['title'],
            'desc': profile['desc'],
            'genres': genres
        }

    return book


def add_seen_book(user_id, book):
    db = get_db()
    db.execute(
        'INSERT INTO seen_books (user_id, book_id)'
        ' VALUES (?, ?)', (user_id, book['id'])
    )
    db.commit()


def match_user(user_id, book):
    db = get_db()

    user2_id = db.execute(
        'SELECT user_id FROM books'
        ' WHERE id = ?', (book['id'],)
    ).fetchone()[0]

    matches = db.execute(
        'SELECT user1_id FROM chatroom'
        ' WHERE user2_id = ?', (user_id,)
    ).fetchall()

    for match in matches:
        if match[0] == user2_id:
            db.execute(
                'UPDATE chatroom'
                ' SET connected = 1'
                ' WHERE user1_id = ? AND user2_id = ?',
                (user2_id, user_id)
            )
            db.commit()
            return

    db.execute(
        'INSERT INTO chatroom (user1_id, user2_id, connected)'
        ' VALUES (?, ?, ?)', (user_id, user2_id, 0)
    )


@bp.route('/', methods=['GET', 'POST'])
@login_required
@has_profile
def index():
    user_id = session.get('user_id')
    book = get_new_book(user_id)
    if book['title'] == '':
        return render_template('books/index.html', book=book)

    if request.method == 'POST':
        if request.form.get('action') == 'cancel':
            add_seen_book(user_id, book)
        elif request.form.get('action') == 'like':
            match_user(user_id, book)
            add_seen_book(user_id, book)
        book = get_new_book(user_id)

    return render_template('books/index.html', book=book)


@bp.route('/profile')
@login_required
@has_profile
def profile():
    user_id = session.get('user_id')
    db = get_db()

    profile = db.execute(
        'SELECT id, title, desc FROM books'
        ' WHERE user_id = ?', (user_id,)
    ).fetchone()

    genre_ids = db.execute(
        'SELECT genre_id FROM book_genres'
        ' WHERE book_id = ?', (profile['id'],)
    ).fetchall()
    genres = []
    for genre_id in genre_ids:
        genres.append(db.execute(
            'SELECT genre FROM genres'
            ' WHERE id = ?', (genre_id[0],)
        ).fetchone()[0])

    book = {
        'title': profile['title'],
        'desc': profile['desc'],
        'genres': genres
    }

    return render_template('books/profile.html', book=book)


@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        user_id = session.get('user_id')
        title = request.form['title']
        desc = request.form['desc']
        genres_string = request.form['genre']
        genres = []
        for genre in genres_string.split(','):
            genres.append(genre.strip().lower())

        db = get_db()
        error = None

        if not title:
            error = 'Title required.'
        elif not desc:
            error = 'Description required.'

        if error is None:
            # delete original profile if it exists
            if db.execute(
                'SELECT id FROM books WHERE user_id = ?', (user_id,)
            ).fetchone() is not None:
                db.execute(
                    'DELETE FROM books WHERE user_id = ?', (user_id,)
                )
                db.commit()

            # add new profile
            db.execute(
                'INSERT INTO books (user_id, title, desc)'
                ' VALUES (?, ?, ?)', (user_id, title, desc)
            )
            db.commit()
            book_id = db.execute(
                'SELECT id FROM books WHERE user_id = ?', (user_id,)
            ).fetchone()[0]

            for genre in genres:
                # if genre doesn't exist, add to genres table
                if db.execute(
                    'SELECT id FROM genres WHERE genre = ?', (genre,)
                ).fetchone() is None:
                    db.execute(
                        'INSERT INTO genres (genre) VALUES (?)', (genre,))
                    db.commit()

                genre_id = db.execute(
                    'SELECT id FROM genres WHERE genre = ?', (genre,)
                ).fetchone()[0]
                db.execute(
                    'INSERT INTO book_genres (book_id, genre_id)'
                    ' VALUES (?, ?)', (book_id, genre_id)
                )
                db.commit()

            return redirect(url_for('books.profile'))

        flash(error)

    return render_template('books/edit_profile.html')
