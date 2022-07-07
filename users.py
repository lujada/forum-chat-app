from db import db
from flask import request, session
from werkzeug.security import check_password_hash, generate_password_hash
import secrets

def login(username, password):
    sql = "SELECT id, password, admin FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        session["login_message"] = "Invalid username!"
        return False
    else:
        hash_value = user.password
        if not check_password_hash(hash_value, password):
            session["login_message"] = "Invalid password!"
            return False
        else:
            session["username"] = username
            session["userid"] = user.id
            session["admin"] = user.admin
            session["login_message"] = " "
            session["csrf_token"] = secrets.token_hex(16)
            return True

def create_user(username, password, admin):
    sql = "SELECT username from users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    unique = result.fetchall()
    if unique != []:
        session["login_message"] = "The username is already taken!"
        return False
    if len(password) <= 2:
        session["login_message"] = "The password is too short!"
        return False
    if len(username) <= 2:
        session["login_message"] = "Please enter a username that contains at least 3 characters"
        return False
    else:
        session["admin"] = admin
        hash_value = generate_password_hash(password)
        sql = "INSERT INTO users (username, password, admin) VALUES (:username, :password, :admin)"
        result = db.session.execute(sql, {"username":username, "password":hash_value, "admin":admin})
        db.session.commit()
        session["login_message"] = " "
        return True

def token():
    if session["csrf_token"] != request.form["csrf_token"]:
        return False
    else:
        return True

def admin():
    if session["admin"] != True:
        return False
    else:
        return True