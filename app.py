from flask import Flask, render_template, redirect, request, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///database.sqlite3"
app.secret_key = '0987654321'
db = SQLAlchemy(app)


# Model work
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)

with app.app_context():
    # if file doesn't exist then create database
    if not os.path.exists("./instance/database.sqlite3") or not os.path.getsize("./instance/database.sqlite3"):
        db.create_all()


# Flask work
@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ...
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)