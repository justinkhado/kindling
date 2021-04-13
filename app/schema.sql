DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS book_genres;
DROP TABLE IF EXISTS seen_books;

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
    liked       INT         NOT NULL    CHECK (liked IN (0, 1)),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE
);