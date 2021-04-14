PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS book_genres;
DROP TABLE IF EXISTS seen_books;
DROP TABLE IF EXISTS chatroom;
DROP TABLE IF EXISTS messages;

CREATE TABLE users (
    id          INTEGER     PRIMARY KEY     AUTOINCREMENT,
    username    TEXT        UNIQUE          NOT NULL,
    password    TEXT        NOT NULL
);

CREATE TABLE books (
    id          INTEGER     PRIMARY KEY     AUTOINCREMENT,
    user_id     INT         NOT NULL,
    title       TEXT        NOT NULL,
    desc        TEXT        NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE genres (
    id          INTEGER     PRIMARY KEY     AUTOINCREMENT,
    genre       TEXT        NOT NULL
);

CREATE TABLE book_genres (
    book_id     INT         NOT NULL,
    genre_id    INT         NOT NULL,
    FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY(genre_id) REFERENCES genres(id) ON DELETE CASCADE
);

CREATE TABLE seen_books (
    user_id     INT         NOT NULL,
    book_id     INT         NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE
);

CREATE TABLE chatroom (
    id          INTEGER     PRIMARY KEY     AUTOINCREMENT,
    user1_id    INT         NOT NULL,
    user2_id    INT         NOT NULL,
    connected   INT         NOT NULL,
    FOREIGN KEY(user1_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(user2_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE messages (
    id          INTEGER     PRIMARY KEY     AUTOINCREMENT,
    room_id     INT         NOT NULL,
    username    TEXT        NOT NULL,
    message     TEXT        NOT NULL,
    time        TEXT        NOT NULL,
    FOREIGN KEY(room_id) REFERENCES chatroom(id) ON DELETE CASCADE
);