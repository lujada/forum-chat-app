from app import app
from flask import redirect, render_template, request, session
from db import db
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
import users, requests

@app.route("/")
def index():
    areas = requests.areas()
    return render_template("index.html", areas=areas) 

@app.route("/login", methods=["POST"])
def login():
    session["login_message"] = " "
    username = request.form["username"]
    password = request.form["password"]
    if not users.login(username, password):
        print('Login failed')
        return redirect("/")
    users.login(username, password)  
    return redirect("/")

@app.route("/createuser", methods=["POST"])
def create_user():
    username = request.form["username"]
    password = request.form["password"]
    admin = request.form["admin"]
    if users.create_user(username, password, admin):
        users.login(username, password)
        return redirect("/")
    else:
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
    area = requests.area(id)
    posts = requests.posts(area.id)
    return render_template("Areas.html", posts=posts, area=area)

@app.route("/topic/<int:id>")
def topic(id):
    messages = requests.messages(id)
    title = requests.title(id)
    image = requests.image(id)
    return render_template("Messages.html", messages=messages, title=title, image=image)

@app.route("/new_post", methods=["POST"])
def new_post():
    if not users.token():
        return render_template("error.html", error="An error occurred")

    title = request.form["title"] 
    if len(title) > 50:
        return render_template("error.html", error="The title should not exceed 50 characters")

    content = request.form["content"]
    if len(content) > 5000:
        return render_template("error.html", error="Your message is too long! (max 5000 characters)")

    area_name = request.form["name"]
    area_id = requests.area_id(area_name)

    post_id = requests.save_post(area_id, title)
    requests.save_message(post_id, content)
    
    return redirect(f"/topic/{post_id}")

@app.route("/<string:name>/reply", methods=["POST"])
def reply(name:str):
    if not users.token():
        return render_template("error.html", error="An error occurred")

    post_id = request.form["id"] 
    content = request.form["content"]
    requests.save_message(post_id, content)

    return redirect(f"/{name}/{post_id}")

@app.route("/admins")
def admins():
    if users.admin() != True:
        return render_template("error.html", error="An error occurred")
    areas = requests.areas()
    return render_template("Admins.html", areas=areas)

@app.route("/new_area", methods=["POST"])
def add_area():
    content = request.form["content"]
    hidden = request.form["hidden"]
    requests.save_area(content, hidden)
    return redirect("/")

@app.route("/delete/area/<int:id>")
def delete_area(id):
    if users.admin():
        requests.delete_area(id)
        return redirect("/")
    else:
        return render_template("error.html", error="An error occurred")

@app.route("/delete/post/<int:id>")
def delete_post(id):
    try:
        area_id = requests.delete_post(id)
        return redirect(f"/area/{area_id}")
    except:
        return render_template("error.html", error="An error occurred")

@app.route("/delete/messages/<int:id>")
def delete_message(id):
    try:
        post_id = requests.delete_message(id)
        return redirect(f"/topic/{post_id}")
    except:
        return render_template("error.html", error="An error occurred")

@app.route("/save_image_link", methods=["POST"])
def add_photo():
    if not users.token():
        return render_template("error.html", error="An error occurred")
    link = request.form["link"]
    post_id = request.form["post_id"]
    requests.add_photo(link, post_id)
    return redirect(f"/topic/{post_id}")

@app.route("/delete/picture/<int:id>")
def delete_photo(id):
    try:
        post_id = requests.delete_photo(id)
        return redirect(f"/topic/{post_id}")
    except:
        return render_template("error.html", error="An error occurred")