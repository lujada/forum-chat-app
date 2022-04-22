# venv command = venv\Scripts\activate
# flask run

from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")

db = SQLAlchemy(app)

@app.route("/")
def index():
    result = db.session.execute("SELECT area, id FROM areas ORDER BY id")
    areas = result.fetchall()
    return render_template("index.html", areas=areas) 

@app.route("/login", methods=["POST"])
def login():
    session["login_message"] = " "
    username = request.form["username"]
    password = request.form["password"]
    sql = "SELECT id, password, admin FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        session["login_message"] = "Invalid username!"
        return redirect("/")
    else:
        hash_value = user.password
        if not check_password_hash(hash_value, password):
            session["login_message"] = "Invalid password!"
            return redirect("/")
        else:
            session["username"] = username
            session["userid"] = user.id
            session["admin"] = user.admin
            session["login_message"] = " "
            return redirect("/")

@app.route("/createuser", methods=["POST"])
def create_user():
    username = request.form["username"]
    password = request.form["password"]
    admin = request.form["admin"]
    hash_value = generate_password_hash(password)
    sql = "INSERT INTO users (username, password, admin) VALUES (:username, :password, :admin) RETURNING id"
    result = db.session.execute(sql, {"username":username, "password":hash_value, "admin":admin})
    user_id = result.fetchone()[0]
    db.session.commit()
    session["login_message"] = " "
    session["username"] = username
    session["userid"] = user_id
    session["admin"] = admin
    return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    del session["userid"]
    del session["admin"]
    session["login_message"] = " "
    return redirect("/")

@app.route("/newuser")
def new_user():
    return render_template("new_user.html")

@app.route("/area/<int:id>")
def areas(id):
    sql = "SELECT id, area FROM areas WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    area = result.fetchone()

    sql = "SELECT posts.id, posts.title, posts.created, users.username FROM posts, users WHERE area_id=:area_id AND posts.user_id = users.id ORDER BY id DESC"
    result = db.session.execute(sql, {"area_id":area.id})
    posts = result.fetchall()
    return render_template("Areas.html", posts=posts, name=area.area)

@app.route("/topic/<int:id>")
def topic(id):
    sql = "SELECT messages.content, messages.created, users.username FROM messages, users WHERE post_id=:id AND messages.user_id = users.id ORDER BY messages.id DESC"
    result = db.session.execute(sql, {"id":id})
    messages = result.fetchall()
    print(messages, 'msgs')
    
    sql = "SELECT title, id FROM posts WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    title = result.fetchone()
    return render_template("Messages.html", messages=messages, title=title)


@app.route("/new_post", methods=["POST"])
def new_post():
    title = request.form["title"] 
    content = request.form["content"]
    name = request.form["name"]
    sql = "SELECT id FROM areas WHERE area=:name"
    result = db.session.execute(sql, {"name":name})
    area_id = result.fetchone()[0]
    user_id = session["userid"]

    sql = "INSERT INTO posts (area_id, title, created, user_id) VALUES (:area_id, :title, NOW(), :user_id) RETURNING id"
    result = db.session.execute(sql, {"area_id":area_id, "title":title, "user_id":user_id})  
    returned_id = result.fetchone()[0]
    db.session.commit()

    sql = "INSERT INTO messages (post_id, content, created, user_id) VALUES (:post_id, :content, NOW(), :user_id)"
    db.session.execute(sql, {"post_id":returned_id, "content":content, "user_id":user_id})
    db.session.commit()
    
    return redirect(f"/{name}")

@app.route("/<string:name>/reply", methods=["POST"])
def reply(name:str):
    post_id = request.form["id"] 
    content = request.form["content"]
    user_id = session["userid"]

    sql = "INSERT INTO messages (post_id, content, created, user_id) VALUES (:post_id, :content, NOW(), :user_id)"
    db.session.execute(sql, {"post_id":post_id, "content":content, "user_id":user_id})
    db.session.commit()

    return redirect(f"/{name}/{post_id}")

@app.route("/admins")
def admins():
    result = db.session.execute("SELECT area, id FROM areas ORDER BY id")
    areas = result.fetchall()
    return render_template("Admins.html", areas=areas)

@app.route("/delete/area/<int:id>")
def delete_area(id):
    sql = "DELETE FROM areas WHERE id=:id"
    db.session.execute(sql, {"id":id})
    db.session.commit()
    return redirect("/")


@app.route("/send", methods=["POST"])
def send():
    content = request.form["content"]
    sql = "INSERT INTO messages (content) VALUES (:content)"
    db.session.execute(sql, {"content":content})
    db.session.commit()
    return redirect("/")

@app.route("/new_area", methods=["POST"])
def add_area():
    content = request.form["content"]
    hidden = request.form["hidden"]
    print(content, "content", hidden, "hidden")

    sql = "INSERT INTO areas (area, hidden) VALUES (:content, :hidden)"
    db.session.execute(sql, {"content": content, "hidden":hidden})
    db.session.commit()
    return redirect("/")