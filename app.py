from flask import Flask, render_template, redirect, request, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///database.sqlite3"
app.secret_key = '0987654321'
db = SQLAlchemy(app)


# Model work
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    dob = db.Column(db.Date)
    score = db.relationship("Score", backref="user")

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String())
    chapter = db.relationship('Chapter', backref='subject')

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String())
    quiz = db.relationship('Quiz', backref="chapter")

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.id"), nullable=False)
    name = db.Column(db.String(), nullable=False)
    quiz_date = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.Time, nullable=False)
    question = db.relationship('QuizQuestion', backref="quiz")
    score = db.relationship('Score', backref="quiz")

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    statement = db.Column(db.String(), nullable=False, unique=True)
    option1 = db.Column(db.String(), nullable=False)
    option2 = db.Column(db.String(), nullable=False)
    option3 = db.Column(db.String(), nullable=False)
    option4 = db.Column(db.String(), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)
    quiz = db.relationship("QuizQuestion", backref="question")

class QuizQuestion(db.Model):
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), primary_key=True, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), primary_key=True, nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    attempt_time = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    user_score = db.Column(db.Integer, nullable=False)

with app.app_context():
    # if file doesn't exist then create database
    if not os.path.exists("./instance/database.sqlite3") or not os.path.getsize("./instance/database.sqlite3"):
        db.create_all()

# Flask work
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        admin = Admin.query.filter_by(username=username, password=password).first()
        user = User.query.filter_by(username=username, password=password).first()
        if admin:
            session["username"] = username
            session["password"] = password
            return redirect(url_for("admin"))
        elif user:
            session["username"] = username
            session["password"] = password
            return redirect(url_for("user", username=username))
        else:
            flash("Invalid credentials", 'error')
            return redirect("/")
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        try:
            dob = datetime.strptime(request.form.get("dob"), "%Y-%m-%d").date()
        except ValueError:
            flash("Enter a valid date of birth", 'error')
            return redirect(url_for("signup"))
        username = request.form.get("username")
        password = request.form.get("password")

        # verify and add user credentials then redirect to login
        # if user's username already exist in admin or user
        admin = Admin.query.filter_by(username=username).first()
        user = User.query.filter_by(username=username).first()
        if admin or user:
            flash("Please choose a different username!", 'error')
            return redirect(url_for("signup"))

        db.session.add(User(name=name, dob=dob, username=username, password=password))
        db.session.commit()
        flash("Successfully signed up!", 'success')
        return redirect(url_for("index"))
    return render_template("signup.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/<username>")
def user(username):
    return render_template("user.html", username=username)

if __name__ == "__main__":
    app.run(debug=True)