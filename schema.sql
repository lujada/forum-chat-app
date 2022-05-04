CREATE TABLE users (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT, admin BOOLEAN);
CREATE TABLE areas (id SERIAL PRIMARY KEY, area TEXT, hidden BOOLEAN);
CREATE TABLE posts (id SERIAL PRIMARY KEY, area_id INTEGER REFERENCES areas(id), title TEXT, created TIMESTAMP, user_id INTEGER REFERENCES user(id));
CREATE TABLE messages (id SERIAL PRIMARY KEY, post_id INTEGER REFERENCES posts(id), content TEXT, created TIMESTAMP, user_id INTEGER REFERENCES users(id));
CREATE TABLE photos (id SERIAL PRIMARY KEY, link TEXT, topic_id INTEGER REFERENCES posts(id));