import os
from flask import (
    Blueprint, flash, redirect, render_template, session, request, url_for
)
from app.books_helper import (
    add_genre, add_profile, add_seen_book, allowed_file, delete_profile,
    get_filename, get_genres_from_id, get_new_book, has_profile, match_user,
    upload_file
)
from app.auth import login_required
from app.db import get_db

from app import app, ALLOWED_EXTENSIONS

bp = Blueprint('books', __name__)


@bp.route('/', methods=['GET', 'POST'])
@login_required
@has_profile
def index():
    user_id = session.get('user_id')
    book = get_new_book(user_id)
    if book['title'] == '':
        return render_template('books/index.html', book=book)

    # register if user liked or disliked a profile
    if request.method == 'POST':
        if request.form.get('action') == 'cancel':
            add_seen_book(user_id, book)
        elif request.form.get('action') == 'like':
            match_user(user_id, book)
            add_seen_book(user_id, book)
        book = get_new_book(user_id)

    has_image = book['title'] != ''

    filename = get_filename(book['user_id'])

    return render_template('books/index.html', book=book, has_image=has_image, filename=filename)


@bp.route('/profile')
@login_required
@has_profile
def profile():
    '''
    display user profile
    '''
    user_id = session.get('user_id')
    db = get_db()

    profile = db.execute(
        'SELECT id, title, desc FROM books'
        ' WHERE user_id = ?', (user_id,)
    ).fetchone()

    genres = get_genres_from_id(profile['id'], db)

    book = {
        'title': profile['title'],
        'desc': profile['desc'],
        'genres': genres
    }

    filename = get_filename(user_id)

    return render_template('books/profile.html', book=book, filename=filename)


@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        file = request.files['image']
        upload_file(file)

        # get profile data
        user_id = session.get('user_id')
        title = request.form['title']
        desc = request.form['desc']
        genres_string = request.form['genre']
        genres = []
        for genre in genres_string.split(','):
            genres.append(genre.strip().lower())

        error = None
        if not title:
            error = 'Title required.'
        elif not desc:
            error = 'Description required.'

        # remove old user profile and add new user profile
        if error is None:
            db = get_db()
            delete_profile(db, user_id)
            add_profile(db, user_id, title, desc)
            book_id = db.execute(
                'SELECT id FROM books WHERE user_id = ?', (user_id,)
            ).fetchone()[0]
            add_genre(db, book_id, genres)

            return redirect(url_for('books.profile'))

        flash(error)

    return render_template('books/edit_profile.html')
