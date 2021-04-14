import os
from flask import Flask, render_template
from flask_socketio import SocketIO

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'profile_images')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'data.sqlite'),
        UPLOAD_FOLDER=UPLOAD_FOLDER
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(os.path.join(app.instance_path))
    except OSError:
        pass
    
    return app

app = create_app()
socketio = SocketIO(app, cors_allowed_origins='*')