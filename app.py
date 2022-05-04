# venv command = venv\Scripts\activate
# flask run

from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from sqlalchemy import null
from werkzeug.security import check_password_hash, generate_password_hash
import secrets

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")

db = SQLAlchemy(app)

@app.route("/")
def index():
    result = db.session.execute("SELECT area, id, hidden FROM areas ORDER BY id")
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
            print(type(session["userid"]), 'useridtype')
            print(session["userid"], 'id login')
            session["admin"] = user.admin
            session["login_message"] = " "
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")

@app.route("/createuser", methods=["POST"])
def create_user():
    username = request.form["username"]
    sql = "SELECT username from users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    unique = result.fetchall()
    if unique != []:
        session["login_message"] = "The username is already taken!"
        return redirect("/")

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
    print(type(session["userid"]), 'userid')
    print(session["userid"], 'id create')
    session["admin"] = bool(admin)
    session["csrf_token"] = secrets.token_hex(16)
    return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    del session["userid"]
    del session["admin"]
    session["login_message"] = " "
    session["csrf_token"] = ""  
    return redirect("/")

@app.route("/newuser")
def new_user():
    return render_template("new_user.html")

@app.route("/area/<int:id>")
def areas(id):
    sql = "SELECT id, area FROM areas WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    area = result.fetchone()

    sql = "SELECT posts.id, posts.title, posts.created, posts.user_id, users.username FROM posts, users WHERE area_id=:area_id AND posts.user_id = users.id ORDER BY id DESC"
    result = db.session.execute(sql, {"area_id":area.id})
    posts = result.fetchall()
    return render_template("Areas.html", posts=posts, name=area.area)

@app.route("/topic/<int:id>")
def topic(id):
    sql = "SELECT messages.id, messages.content, messages.created, messages.user_id, users.username FROM messages, users WHERE post_id=:id AND messages.user_id = users.id ORDER BY messages.id DESC"
    result = db.session.execute(sql, {"id":id})
    messages = result.fetchall()
    
    sql = "SELECT title, id FROM posts WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    title = result.fetchone()

    sql = "SELECT link FROM photos WHERE topic_id=:id"
    result = db.session.execute(sql, {"id":id})
    image = result.fetchone()
    return render_template("Messages.html", messages=messages, title=title, image=image)


@app.route("/new_post", methods=["POST"])
def new_post():
    if session["csrf_token"] != request.form["csrf_token"]:
        return render_template("error.html", error="An error occurred")
    title = request.form["title"] 
    if len(title) > 50:
        return render_template("error.html", error="The title should not exceed 50 characters")
    content = request.form["content"]
    if len(content) > 5000:
        return render_template("error.html", error="Your message is too long! (max 5000 characters)")
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
    
    return redirect(f"/area/{area_id}")

@app.route("/<string:name>/reply", methods=["POST"])
def reply(name:str):
    if session["csrf_token"] != request.form["csrf_token"]:
        return render_template("error.html", error="An error occurred")
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

@app.route("/delete/post/<int:id>")
def delete_post(id):
    sql = "UPDATE posts SET title = NULL WHERE id=:id"
    db.session.execute(sql, {"id":id})
    db.session.commit()
    return redirect("/")

@app.route("/delete/messages/<int:id>")
def delete_message(id):
    sql = "UPDATE messages SET content = NULL WHERE id=:id"
    db.session.execute(sql, {"id":id})
    db.session.commit()
    return redirect("/")

@app.route("/save_image_link", methods=["POST"])
def add_photo():
    link = request.form["link"]
    post_id = request.form["post_id"]
    sql = "INSERT INTO photos  (link, topic_id) VALUES (:link, :post_id)"
    db.session.execute(sql, {"link":link, "post_id":post_id})
    db.session.commit()
    return redirect("/")



@app.route("/send", methods=["POST"])
def send():
    if session["csrf_token"] != request.form["csrf_token"]:
        return render_template("error.html", error="An error occurred")
    content = request.form["content"]
    sql = "INSERT INTO messages (content) VALUES (:content)"
    db.session.execute(sql, {"content":content})
    db.session.commit()
    return redirect("/")

@app.route("/new_area", methods=["POST"])
def add_area():
    content = request.form["content"]
    hidden = request.form["hidden"]

    sql = "INSERT INTO areas (area, hidden) VALUES (:content, :hidden)"
    db.session.execute(sql, {"content": content, "hidden":hidden})
    db.session.commit()
    return redirect("/")

@app.route("/search")
def search():
    return render_template("search.html") 