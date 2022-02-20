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
    result = db.session.execute("SELECT area FROM areas ORDER BY id")
    areas = result.fetchall()
    return render_template("index.html", areas=areas) 

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    sql = "SELECT id, password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        print("invalid username")
    else:
        hash_value = user.password
        if check_password_hash(hash_value, password):
            print('correct username and password')
        else:
            print('invalid password')
    session["username"] = username
    session["userid"] = user.id
    return redirect("/")

@app.route("/createuser", methods=["POST"])
def create_user():
    username = request.form["username"]
    password = request.form["password"]
    hash_value = generate_password_hash(password)
    print(hash_value)
    sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
    db.session.execute(sql, {"username":username, "password":hash_value})
    db.session.commit()
    return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    del session["userid"]
    return redirect("/")

@app.route("/newuser")
def new_user():
    return render_template("new_user.html")

@app.route("/<string:name>")
def areas(name:str):
    sql = "SELECT id FROM areas WHERE area=:name"
    result = db.session.execute(sql, {"name":name})
    area_id = result.fetchone()[0]

    sql = "SELECT id, title, created FROM posts WHERE area_id=:area_id ORDER BY id DESC"
    result = db.session.execute(sql, {"area_id":area_id})
    posts = result.fetchall()
    return render_template("Areas.html", posts=posts, name=name)

@app.route("/<string:name>/<int:id>")
def topic(name:str, id):
    sql = "SELECT content, created FROM messages WHERE post_id=:id ORDER BY id DESC"
    result = db.session.execute(sql, {"id":id})
    messages = result.fetchall()
    
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
    print(title, content, area_id)

    sql = "INSERT INTO posts (area_id, title, created) VALUES (:area_id, :title, NOW()) RETURNING id"
    result = db.session.execute(sql, {"area_id":area_id, "title":title})  
    returned_id = result.fetchone()[0]
    db.session.commit()

    sql = "INSERT INTO messages (post_id, content, created) VALUES (:post_id, :content, NOW())"
    db.session.execute(sql, {"post_id":returned_id, "content":content})
    db.session.commit()
    
    return redirect(f"/{name}")

@app.route("/<string:name>/reply", methods=["POST"])
def reply(name:str):
    post_id = request.form["id"] 
    content = request.form["content"]
    user_id = session["userid"]

    sql = "INSERT INTO messages (post_id, content, created) VALUES (:post_id, :content, NOW())"
    db.session.execute(sql, {"post_id":post_id, "content":content})
    db.session.commit()

    return redirect(f"/{name}/{post_id}")


@app.route("/send", methods=["POST"])
def send():
    content = request.form["content"]
    sql = "INSERT INTO messages (content) VALUES (:content)"
    db.session.execute(sql, {"content":content})
    db.session.commit()
    return redirect("/")