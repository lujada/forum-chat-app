from db import db
from flask import request, session
from werkzeug.security import check_password_hash, generate_password_hash
import secrets

def areas():
    result = db.session.execute("SELECT area, id, hidden FROM  areas WHERE area IS NOT NULL ORDER BY id")
    areas = result.fetchall()
    return areas

def area(id):
    sql = "SELECT id, area FROM areas WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    area = result.fetchone()
    return area

def posts(id):
    sql = "SELECT posts.id, posts.title, posts.created, posts.user_id, users.username FROM posts, users WHERE area_id=:area_id AND posts.user_id = users.id ORDER BY id DESC"
    result = db.session.execute(sql, {"area_id":id})
    posts = result.fetchall()
    return posts

def messages(id):
    sql = "SELECT messages.id, messages.content, messages.created, messages.user_id, users.username FROM messages, users WHERE post_id=:id AND messages.user_id = users.id ORDER BY messages.id DESC"
    result = db.session.execute(sql, {"id":id})
    messages = result.fetchall()
    return messages

def title(id): 
    sql = "SELECT title, id, user_id FROM posts WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    title = result.fetchone()
    return title

def image(id):
    sql = "SELECT link, id FROM photos WHERE topic_id=:id"
    result = db.session.execute(sql, {"id":id})
    image = result.fetchone()
    return image

def area_id(area_name):
    sql = "SELECT id FROM areas WHERE area=:name"
    result = db.session.execute(sql, {"name":area_name})
    area_id = result.fetchone()[0]
    return area_id

def save_post(area_id, title):
    user_id = session["userid"]
    sql = "INSERT INTO posts (area_id, title, created, user_id) VALUES (:area_id, :title, NOW(), :user_id) RETURNING id"
    result = db.session.execute(sql, {"area_id":area_id, "title":title, "user_id":user_id})  
    post_id = result.fetchone()[0]
    db.session.commit()
    return post_id

def save_message(post_id, content):
    user_id = session["userid"]
    sql = "INSERT INTO messages (post_id, content, created, user_id) VALUES (:post_id, :content, NOW(), :user_id)"
    db.session.execute(sql, {"post_id":post_id, "content":content, "user_id":user_id})
    db.session.commit()

def save_area(content, hidden):
    sql = "INSERT INTO areas (area, hidden) VALUES (:content, :hidden)"
    db.session.execute(sql, {"content": content, "hidden":hidden})
    db.session.commit()

def delete_area(id):
    sql = "UPDATE areas SET area = NULL WHERE id=:id"
    db.session.execute(sql, {"id":id})
    db.session.commit()

def delete_post(id):
    sql = "SELECT user_id FROM posts WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    user_id = result.fetchone()[0]
    if session["userid"] != user_id and session["admin"] == False:
        return False

    sql = "UPDATE posts SET title = NULL WHERE id=:id RETURNING area_id"
    result = db.session.execute(sql, {"id":id})
    area_id = result.fetchone()[0]
    db.session.commit()
    return area_id

def delete_message(id):
    sql = "SELECT user_id FROM messages WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    user_id = result.fetchone()[0]
    if session["userid"] != user_id and session["admin"] == False:
        return False

    sql = "UPDATE messages SET content = NULL WHERE id=:id RETURNING post_id"
    result = db.session.execute(sql, {"id":id})
    post_id = result.fetchone()[0]
    db.session.commit()
    return post_id

def add_photo(link, post_id):
    sql = "INSERT INTO photos  (link, topic_id) VALUES (:link, :post_id)"
    db.session.execute(sql, {"link":link, "post_id":post_id})
    db.session.commit()
    return True

def delete_photo(id):
    sql = "UPDATE photos SET link = NULL WHERE id=:id RETURNING topic_id"
    result = db.session.execute(sql, {"id":id})
    post_id = result.fetchone()[0]
    db.session.commit()
    return post_id



