from flask import Flask
from flask import render_template
app = Flask(__name__)


@app.route("/")
def hello():
    return render_template('home.html')


@app.route("/login/")
def login():
    return render_template('login.html')
