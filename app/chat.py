from flask import (
    Blueprint, flash, redirect, render_template, session, request, url_for
)
from flask_socketio import send, emit, join_room, leave_room
from app.auth import login_required
from app.books import has_profile
from app.db import get_db
from app import socketio

bp = Blueprint('chat', __name__, url_prefix='/chat')


def get_username(user_id):
    username = get_db().execute(
        'SELECT username FROM users'
        ' WHERE id = ?', (user_id,)
    ).fetchone()[0]

    return username


def get_matches(user_id):
    db = get_db()
    matches_query = db.execute(
        'SELECT user1_id, user2_id'
        ' FROM chatroom'
        ' WHERE (user1_id = ? OR user2_id = ?) AND'
        '  connected = 1', (user_id, user_id)
    ).fetchall()

    matches = []
    for match in matches_query:
        if match[0] == user_id:
            matches.append(
                {'id': match[1], 'username': get_username(match[1])})
        elif match[1] == user_id:
            matches.append(
                {'id': match[0], 'username': get_username(match[0])})

    return matches


def get_messages(room_id):
    message_query = get_db().execute(
        'SELECT username, message'
        ' FROM messages'
        ' WHERE room_id = ?'
        ' ORDER BY time', (room_id,)
    ).fetchall()

    messages = []
    for row in message_query:
        messages.append({
            'username': row['username'],
            'message': row['message']
        })

    return messages


@bp.route('/matches', methods=['GET', 'POST'])
@login_required
def matches():
    '''
    show all matches with user
    '''
    if request.method == 'POST':
        room = request.form['room']
        session['room'] = room
        return redirect(url_for('chat.chatroom'))

    user_id = session.get('user_id')
    matches = get_matches(user_id)

    return render_template('chat/matches.html', user_id=user_id, matches=matches)


@bp.route('/chatroom')
def chatroom():
    '''
    private chatroom for matches
    '''
    if 'room' not in session:
        return redirect(url_for('chat.matches'))

    room = session['room']
    user_id = session.get('user_id')
    username = get_username(user_id)

    ids = room.split('_')
    other_user = ''
    if str(user_id) == ids[0]:
        other_user = get_username(ids[1])
    elif str(user_id) == ids[1]:
        other_user = get_username(ids[0])

    data = {
        'user_id': user_id,
        'username': username,
        'other_user': other_user,
        'room': room,
        'messages': get_messages(room)
    }

    return render_template('chat/chatroom.html', data=data)


@socketio.on('send_message', namespace='/chat/chatroom')
def message(data):
    '''
    send message to room using user input
    '''
    db = get_db()
    db.execute(
        'INSERT INTO messages (room_id, username, message, time)'
        ' VALUES (?, ?, ?, CURRENT_TIMESTAMP)',
        (session['room'], data['username'], data['message'])
    )
    db.commit()

    data = {
        'username': data['username'],
        'message': data['message']
    }
    emit('send message', data, to=session['room'])


@socketio.on('join', namespace='/chat/chatroom')
def on_join(data):
    '''
    add user to room
    '''
    username = data['username']
    room = session['room']
    join_room(room)
