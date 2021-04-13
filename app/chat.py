from flask import (
    Blueprint, flash, redirect, render_template, session, request, url_for
)
from flask_socketio import join_room, leave_room
from app.auth import login_required
from app.books import has_profile
from app.db import get_db

bp = Blueprint('chat', __name__, url_prefix='/chat')

@bp.route('/matches')
def matches():
    return render_template('chat/matches.html')