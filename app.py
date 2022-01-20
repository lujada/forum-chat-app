from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Heipparallaa!"

@app.route("/testi")
def test():
    content = ""
    for i in range(100):
        content += str(i) + " "
    return content