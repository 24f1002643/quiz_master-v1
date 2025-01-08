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
    question = db.relationship('Chapterwisequestion', backref='chapter')

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.id"), nullable=False)
    name = db.Column(db.String(), nullable=False)
    quiz_date = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.Time, nullable=False)
    question = db.relationship('Quizwisequestion', backref="quiz")
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
    chapter = db.relationship('Chapterwisequestion', backref="question")
    quiz = db.relationship('Quizwisequestion', backref="question")

class Chapterwisequestion(db.Model):
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), primary_key=True, nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.id"), primary_key=True, nullable=False)

class Quizwisequestion(db.Model):
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
        db.session.add(Admin(username="admin", password="admin"))
        db.session.commit()


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

@app.route("/admin/dashboard")
def admin():
    if 'username' in session:
        admin = Admin.query.filter_by(username=session["username"]).first()
        if not admin:
            flash("Invalid Credentials!", "error")
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))

    subjects = Subject.query.all()
    questions = Question.query.all()
    chapterwisequestions = Chapterwisequestion.query.all()
    subject_data = []
    for subject in subjects:
        chapters = Chapter.query.filter_by(subject_id=subject.id).all()
        chapter = [
            {
                "id": chapter.id,
                "name": chapter.name,
                "description": chapter.description,
                "number_of_questions": Chapterwisequestion.query.filter_by(chapter_id=chapter.id).count(),
                "questions": db.session.query(Question).join(Chapterwisequestion).filter(Question.id == Chapterwisequestion.question_id).filter_by(chapter_id=chapter.id).all()
            }
            for chapter in chapters
        ]
        subject_data.append({
            "id": subject.id,
            "name": subject.name,
            "description": subject.description,
            "chapters": chapter
        })
    
    return render_template("admin.html", subjects=subject_data,
                           questions=questions,
                           chapterwisequestions=chapterwisequestions)

@app.route("/<username>")
def user(username):
    user = User.query.filter_by(username=username).first()
    if user and ('username' in session and username == session["username"]):
        return render_template("user.html", user=user)
    else:
        flash("Invalid credentials!", "error")
        return redirect(url_for("index"))

@app.route("/subject/<action>", methods=["POST"])
@app.route("/subject/<action>/<int:id>", methods=["POST"])
def subject(action, id=None):
    if action == "add":
        db.session.add(Subject(name=request.form.get("name"), description=request.form.get("description")))
        db.session.commit()
        return redirect(url_for("admin"))
    elif action == "update":
        subject = Subject.query.filter_by(id=id).first()
        subject.name = request.form.get(f"subject_name{id}")
        subject.description = request.form.get(f"subject_description{id}")
        db.session.commit()
        return redirect(url_for("admin"))
    elif action == "delete":
        subject = Subject.query.filter_by(id=id).first()
        chapters = Chapter.query.filter_by(subject_id=id).all()
        if subject:
            for chapter in chapters:
                db.session.delete(chapter)
            db.session.delete(subject)
            db.session.commit()
        return redirect(url_for("admin"))
    else:
        flash("Invalid input", "error")
        return redirect(url_for("admin"))
    
@app.route("/chapter/<action>", methods=["POST"])
@app.route("/chapter/<action>/<int:id>", methods=["POST"])
def chapter(action, id=None):
    if action == "add":
        db.session.add(Chapter(name=request.form.get("name"),
                               description=request.form.get("description"),
                               subject_id=request.form.get("subject_id")))
        db.session.commit()
        return redirect(url_for("admin"))
    elif action == "update":
        chapter = Chapter.query.filter_by(id=id).first()
        chapter.name = request.form.get(f"chapter_name{id}")
        chapter.description = request.form.get(f"chapter_description{id}")
        db.session.commit()
        return redirect(url_for("admin"))
    elif action == "delete":
        chapter = Chapter.query.filter_by(id=id).first()
        if chapter:
            db.session.delete(chapter)
            db.session.commit()
        return redirect(url_for("admin"))
    else:
        flash("Invalid input", "error")
        return redirect(url_for("admin"))

@app.route("/question/<action>", methods=["POST"])
@app.route("/question/<action>/<int:id>", methods=["POST"])
def question(action, id=None):
    if action == "add":
        db.session.add(Question(title=request.form.get("title"),
                                statement=request.form.get("statement"),
                                option1=request.form.get("option1"),
                                option2=request.form.get("option2"),
                                option3=request.form.get("option3"),
                                option4=request.form.get("option4"),
                                correct_option=request.form.get("correct_option")))
        question = Question.query.filter_by(statement=request.form.get("statement")).first()
        db.session.add(Chapterwisequestion(question_id=question.id,
                                           chapter_id=request.form.get("chapter_id")))
        db.session.commit()
        return redirect(url_for("admin"))
    elif action == "update":
        question = Question.query.filter_by(id=id).first()
        # To be done
        db.session.commit()
        return redirect(url_for("admin"))
    elif action == "delete":
        question = Question.query.filter_by(id=id).first()
        chapterwisequestions = Chapterwisequestion.query.filter_by(question_id=id).all()
        quizwisequestions = Quizwisequestion.query.filter_by(question_id=id).all()
        if question:
            for questions in chapterwisequestions:
                db.session.delete(questions)
            for questions in quizwisequestions:
                db.session.delete(questions)
            db.session.delete(question)
            db.session.commit()
        return redirect(url_for("admin"))
    else:
        flash("Invalid input", "error")
        return redirect(url_for("admin"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == "__main__":
    app.run(debug=True)