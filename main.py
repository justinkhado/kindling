from app import app, db, auth, books, chat, socketio

db.init_app(app)
app.register_blueprint(auth.bp)
app.register_blueprint(books.bp)
app.add_url_rule('/', endpoint='index')
app.register_blueprint(chat.bp)

if __name__ == '__main__':
    socketio.run(app, debug=True)