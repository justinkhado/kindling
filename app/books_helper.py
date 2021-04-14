import os
import functools
from flask import redirect, session, url_for
from app.db import get_db
from app import app, ALLOWED_EXTENSIONS


def add_genre(db, book_id, genres):
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


def add_profile(db, user_id, title, desc):
    # add new profile
    db.execute(
        'INSERT INTO books (user_id, title, desc)'
        ' VALUES (?, ?, ?)', (user_id, title, desc)
    )
    db.commit()


def add_seen_book(user_id, book):
    db = get_db()
    db.execute(
        'INSERT INTO seen_books (user_id, book_id)'
        ' VALUES (?, ?)', (user_id, book['id'])
    )
    db.commit()


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def delete_profile(db, user_id):
    # delete original profile if it exists
    if db.execute(
        'SELECT id FROM books WHERE user_id = ?', (user_id,)
    ).fetchone() is not None:
        db.execute(
            'DELETE FROM books WHERE user_id = ?', (user_id,)
        )
        db.commit()

def get_filename(id):
    filename = os.path.join('profile_images', str(id) + '.')
    for ext in ALLOWED_EXTENSIONS:
        if os.path.isfile(os.path.join(os.getcwd(), 'app', 'static', filename + ext)):
            filename = filename + ext
            break
    filename = filename.replace('\\', '/')

    return filename


def get_genres_from_id(book_id, db):
    genre_ids = db.execute(
        'SELECT genre_id FROM book_genres'
        ' WHERE book_id = ?', (book_id,)
    ).fetchall()
    genres = []
    for genre_id in genre_ids:
        genres.append(db.execute(
            'SELECT genre FROM genres'
            ' WHERE id = ?', (genre_id[0],)
        ).fetchone()[0])

    return genres


def get_new_book(user_id):
    db = get_db()

    books = db.execute(
        'SELECT id, books.user_id, title, desc'
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
    book = {'user_id': None, 'title': '', 'desc': 'No books left'}
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
            'user_id': profile['user_id'],
            'title': profile['title'],
            'desc': profile['desc'],
            'genres': genres
        }

    return book


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


def upload_file(file):
    user_id = session.get('user_id')
    if file and allowed_file(file.filename):
        extension = file.filename.rsplit('.', 1)[1].lower()
        filename = str(user_id) + '.' + extension
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
