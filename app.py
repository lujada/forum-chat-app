# venv command = venv\Scripts\activate
# flask run

from flask import Flask
from flask import redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from os import getenv

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

@app.route("/")
def index():
    result = db.session.execute("SELECT area FROM areas ORDER BY id")
    areas = result.fetchall()
    return render_template("index.html", areas=areas) 

@app.route("/new")
def new():
    return render_template("new.html")

@app.route("/General")
def General():
    result = db.session.execute("SELECT title, id FROM posts WHERE area_id=1")
    posts = result.fetchall()
    print(posts)
    return render_template("General.html", posts=posts)

@app.route("/General/<int:id>")
def topic(id):
    sql = "SELECT content FROM messages WHERE post_id=:id"
    result = db.session.execute(sql, {"id":id})
    messages = result.fetchall()
    
    sql = "SELECT title FROM posts WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    title = result.fetchone()
    return render_template("Messages.html", messages=messages, title=title.title)


@app.route("/Music")
def Music():
    return render_template("Music.html")

@app.route("/Events")
def Events():
    return render_template("Events.html")

@app.route("/Other")
def Other():
    return render_template("Other.html")

@app.route("/Admin")
def Admin():
    return render_template("Admin.html")





@app.route("/send", methods=["POST"])
def send():
    content = request.form["content"]
    sql = "INSERT INTO messages (content) VALUES (:content)"
    db.session.execute(sql, {"content":content})
    db.session.commit()
    return redirect("/")