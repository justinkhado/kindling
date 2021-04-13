from flask import (
    Blueprint, flash, redirect, render_template, session, request, url_for
)
from app.auth import login_required
from app.db import get_db

bp = Blueprint('books', __name__)


@bp.route('/')
@login_required
def index():
    user_id = session.get('user_id')
    db = get_db()

    has_profile = db.execute(
        'SELECT * FROM books WHERE user_id = ?', (user_id,)
    ).fetchone()

    if has_profile is None:
        return redirect(url_for('books.edit_profile'))

    books = db.execute(
        'SELECT id, seen_books.user_id, title, desc'
        ' FROM books'
        ' LEFT JOIN seen_books'
        '  ON books.id = seen_books.book_id'
        ' WHERE id != (SELECT id FROM books WHERE user_id = ?)',
        (user_id,)
    ).fetchall()

    profile = None
    for book in books:
        if book['user_id'] is None:
            profile = book
            break

    genres = []
    book = None
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
            'title': profile['title'],
            'desc': profile['desc'],
            'genres': genres
        }

    return render_template('books/index.html', book=book)


@bp.route('/profile')
@login_required
def profile():
    user_id = session.get('user_id')
    db = get_db()

    has_profile = db.execute(
        'SELECT * FROM books WHERE user_id = ?', (user_id,)
    ).fetchone()

    if has_profile is None:
        return redirect(url_for('books.edit_profile'))

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
