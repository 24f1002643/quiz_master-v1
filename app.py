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
    blocked = db.Column(db.Boolean, default=0)
    score = db.relationship("Score", backref="user")

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String())
    chapter = db.relationship('Chapter', backref='subject')
    quiz = db.relationship('Quiz', backref="subject")

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String())
    question = db.relationship('Question', backref='chapter')

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)
    name = db.Column(db.String(), nullable=False)
    quiz_date = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.Time, nullable=False)
    question = db.relationship('Quizwisequestion', backref="quiz")
    score = db.relationship('Score', backref="quiz")

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    statement = db.Column(db.String(), nullable=False, unique=True)
    option1 = db.Column(db.String(), nullable=False)
    option2 = db.Column(db.String(), nullable=False)
    option3 = db.Column(db.String(), nullable=False)
    option4 = db.Column(db.String(), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)
    quiz = db.relationship('Quizwisequestion', backref="question")

class Quizwisequestion(db.Model):
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), primary_key=True, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), primary_key=True, nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    start_time = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    end_time = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    user_score = db.Column(db.Integer, nullable=False)

with app.app_context():
    # if file doesn't exist then create database
    if not os.path.exists("./instance/database.sqlite3") or not os.path.getsize("./instance/database.sqlite3"):
        db.create_all()
        db.session.add(Admin(username="admin", password="admin"))
        db.session.add(User(name="Samar", username="samar", password="4554", dob=datetime.strptime("2004-08-22", r'%Y-%m-%d').date()))
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
            if user.blocked == 0:
                session["username"] = username
                session["password"] = password
                return redirect(url_for("user", username=username))
            else:
                flash("You are blocked from using the site!", "error")
                return redirect(url_for("index"))
        else:
            flash("Invalid credentials", "error")
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
    subject_data = []
    for subject in subjects:
        chapters = [
            {
                "id": chapter.id,
                "name": chapter.name,
                "description": chapter.description,
                "number_of_questions": Question.query.filter_by(chapter_id=chapter.id).count(),
                "questions": Question.query.filter_by(chapter_id=chapter.id).all()
            }
            for chapter in Chapter.query.filter_by(subject_id=subject.id).all()
        ]
        subject_data.append({
            "id": subject.id,
            "name": subject.name,
            "description": subject.description,
            "chapters": chapters
        })
    
    return render_template("admin.html", subjects=subject_data)

@app.route("/admin/dashboard/search/<type>")
def admin_search(type):
    query = request.args.get("q").strip()
    if type == "subject":
        subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
        subject_data = []
        for subject in subjects:
            chapters = [
                {
                    "id": chapter.id,
                    "name": chapter.name,
                    "description": chapter.description,
                    "number_of_questions": Question.query.filter_by(chapter_id=chapter.id).count(),
                    "questions": Question.query.filter_by(chapter_id=chapter.id).all()
                }
                for chapter in Chapter.query.filter_by(subject_id=subject.id).all()
            ]
            subject_data.append({
                "id": subject.id,
                "name": subject.name,
                "description": subject.description,
                "chapters": chapters
            })
        return render_template("subject.html", subjects=subject_data, search=True)
    elif type == "quiz":
        subjects = Subject.query.all()
        subject_data = []
        for subject in subjects:
            quizzes = [
                {
                    "id": quiz.id,
                    "name": quiz.name,
                    "quiz_date": quiz.quiz_date,
                    "time_duration": quiz.time_duration,
                    "quizwisequestions": db.session.query(Question).join(Quizwisequestion).filter(Question.id == Quizwisequestion.question_id).filter_by(quiz_id=quiz.id).all(),
                    "subjectwisequestions": db.session.query(Question.statement, Question.id).join(Chapter).join(Subject).filter(Question.chapter_id == Chapter.id).filter(Subject.id == Chapter.subject_id).filter(Subject.id == subject.id).all()
                }
                for quiz in Quiz.query.filter(db.or_(Quiz.name.ilike(f"%{query}%"), Quiz.quiz_date.ilike(f"%{query}%"))).filter_by(subject_id=subject.id).all()
            ]
            subject_data.append({
                "id": subject.id,
                "name": subject.name,
                "description": subject.description,
                "quizzes": quizzes
            })

        return render_template("quiz.html", subjects=subject_data, search=True, current_time=datetime.now().date())
    elif type == "user":
        users = User.query.filter(db.or_(User.name.ilike(f"%{query}%"), User.username.ilike(f"%{query}%"), User.dob.ilike(f"%{query}%"))).all()
        return render_template("users.html", users=users, search=True)

@app.route("/admin/quiz")
def admin_quiz():
    if 'username' in session:
        admin = Admin.query.filter_by(username=session["username"]).first()
        if not admin:
            flash("Invalid Credentials!", "error")
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))
    
    subjects = Subject.query.all()
    subject_data = []
    for subject in subjects:
        quizzes = [
            {
                "id": quiz.id,
                "name": quiz.name,
                "quiz_date": quiz.quiz_date,
                "time_duration": quiz.time_duration,
                "quizwisequestions": db.session.query(Question).join(Quizwisequestion).filter(Question.id == Quizwisequestion.question_id).filter_by(quiz_id=quiz.id).all(),
                "subjectwisequestions": db.session.query(Question.statement, Question.id).join(Chapter).join(Subject).filter(Question.chapter_id == Chapter.id).filter(Subject.id == Chapter.subject_id).filter(Subject.id == subject.id).all()
            }
            for quiz in Quiz.query.filter_by(subject_id=subject.id).all()
        ]
        subject_data.append({
            "id": subject.id,
            "name": subject.name,
            "description": subject.description,
            "quizzes": quizzes
        })

    return render_template("admin_quiz.html", subjects=subject_data, current_time=datetime.now().date())

@app.route("/admin/users")
@app.route("/admin/user/<action>/<int:id>", methods=["POST"])
def admin_users(action=None, id=None):
    if request.method == "POST":
        if action == "block":
            user = User.query.filter_by(id=id).first()
            if user:
                user.blocked = 1
                db.session.commit()
        elif action == "unblock":
            user = User.query.filter_by(id=id).first()
            if user:
                user.blocked = 0
                db.session.commit()
        elif action == "delete":
            user = User.query.filter_by(id=id).first()
            if user:
                db.session.delete(user)
                db.session.commit()
        return redirect("/admin/users")

    if 'username' in session:
        admin = Admin.query.filter_by(username=session["username"]).first()
        if not admin:
            flash("Invalid Credentials!", "error")
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))
    
    users = User.query.all()
    return render_template("admin_users.html", users=users)

@app.route("/<username>")
def user(username):
    user = User.query.filter_by(username=username).first()
    if user and ('username' in session and username == session["username"]):
        data = db.session.query(
            Quiz.id.label("quiz_id"),
            Subject.id.label("subject_id"),
            Quiz.name.label("quiz_name"),
            Subject.name.label("subject_name"),
            Quiz.quiz_date,
            Quiz.time_duration
        ).join(Subject, Quiz.subject_id == Subject.id).filter(
            Quiz.quiz_date > datetime.now()
        ).all()
        subject_data = []
        for row in data:
            subject_data.append({
                "subject_id": row.subject_id,
                "subject_name": row.subject_name,
                "quiz_id": row.quiz_id,
                "quiz_name": row.quiz_name,
                "quiz_date": row.quiz_date,
                "time_duration": row.time_duration,
                "no_of_questions": Quizwisequestion.query.filter_by(quiz_id=row.quiz_id).count()
            })
        return render_template("user.html", user=user, data=subject_data)
    else:
        flash("Invalid credentials!", "error")
        return redirect(url_for("index"))

@app.route("/search")
def user_quiz():
    query = request.args.get("q").strip()
    data = db.session.query(
        Quiz.id.label("quiz_id"),
        Quiz.name.label("quiz_name"),
        Subject.name.label("subject_name"),
        Quiz.quiz_date,
        Quiz.time_duration
    ).join(Subject, Quiz.subject_id == Subject.id).filter(
        db.and_(
            Quiz.quiz_date > datetime.now(),
            db.or_(
                Quiz.name.ilike(f"%{query}%"),
                Subject.name.ilike(f"%{query}%"),
                Quiz.quiz_date.ilike(f"%{query}%")
            )
        )
    ).all()
    subject_data = []
    for row in data:
        subject_data.append({
            "subject_name": row.subject_name,
            "quiz_id": row.quiz_id,
            "quiz_name": row.quiz_name,
            "quiz_date": row.quiz_date,
            "time_duration": row.time_duration,
            "no_of_questions": Quizwisequestion.query.filter_by(quiz_id=row.quiz_id).count()
        })
    return render_template("upcoming_quiz.html", data=subject_data, search=True)

@app.route("/<username>/score")
def user_score(username):
    user = User.query.filter_by(username=username).first()
    if not user or (not 'username' in session or username != session["username"]):
        flash("Invalid credentials!", "error")
        return redirect(url_for("index"))
    
    data = []
    tmp_data = db.session.query(
        Quiz.id.label("quiz_id"),
        Quiz.name.label("quiz_name"),
        Subject.name.label("subject_name"),
        Quiz.quiz_date,
        Quiz.time_duration,
        Score.start_time,
        Score.end_time,
        Score.user_score
    ).join(Subject, Quiz.subject_id == Subject.id
    ).join(Score, Score.quiz_id == Quiz.id).filter(Score.user_id==User.id).all()

    for row in tmp_data:
        data.append({
            "quiz_id":row.quiz_id,
            "quiz_name":row.quiz_name,
            "subject_name":row.subject_name,
            "no_of_questions": Quizwisequestion.query.filter_by(quiz_id=row.quiz_id).count(),
            "quiz_date":row.quiz_date,
            "time_duration":row.time_duration,
            "attempt_time":row.end_time-row.start_time,
            "user_score":row.user_score
        })
    return render_template("user_score.html", user=user, data=data)

@app.route("/<username>/score/search")
def user_score_search(username):
    query = request.args.get("q").strip()

    data = []
    tmp_data = db.session.query(
        Quiz.id.label("quiz_id"),
        Quiz.name.label("quiz_name"),
        Subject.name.label("subject_name"),
        Quiz.quiz_date,
        Quiz.time_duration,
        Score.start_time,
        Score.end_time,
        Score.user_score
    ).join(Subject, Quiz.subject_id == Subject.id
    ).join(Score, Score.quiz_id == Quiz.id).filter(Score.user_id==User.id).filter(
        db.or_(
                Quiz.name.ilike(f"%{query}%"),
                Subject.name.ilike(f"%{query}%"),
                Quiz.quiz_date.ilike(f"%{query}%")
            )
    ).all()
    for row in tmp_data:
        data.append({
            "quiz_id":row.quiz_id,
            "quiz_name":row.quiz_name,
            "subject_name":row.subject_name,
            "no_of_questions": Quizwisequestion.query.filter_by(quiz_id=row.quiz_id).count(),
            "quiz_date":row.quiz_date,
            "time_duration":row.time_duration,
            "attempt_time":row.end_time-row.start_time,
            "user_score":row.user_score
        })
    return render_template("quiz_score.html", data=data, search=True)

@app.route("/subject/<action>", methods=["POST"])
@app.route("/subject/<action>/<int:id>", methods=["POST"])
def subject(action, id=None):
    if action == "add":
        db.session.add(Subject(name=request.form.get("name"), description=request.form.get("description")))
        db.session.commit()
    elif action == "update":
        subject = Subject.query.filter_by(id=id).first()
        if subject:
            subject.name = request.form.get(f"subject_name{id}")
            subject.description = request.form.get(f"subject_description{id}")
            db.session.commit()
    elif action == "delete":
        subject = Subject.query.filter_by(id=id).first()
        chapters = Chapter.query.filter_by(subject_id=id).all()
        if subject:
            for chapter in chapters:
                db.session.delete(chapter)
            db.session.delete(subject)
            db.session.commit()
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
    elif action == "update":
        chapter = Chapter.query.filter_by(id=id).first()
        if chapter:
            chapter.name = request.form.get(f"chapter_name{id}")
            chapter.description = request.form.get(f"chapter_description{id}")
            db.session.commit()
    elif action == "delete":
        chapter = Chapter.query.filter_by(id=id).first()
        questions = Question.query.filter_by(chapter_id=id).all()
        quiz = Quiz.query.filter_by(chapter_id=id).all()
        if chapter:
            for ids in questions:
                db.session.delete(ids)
            for ids in quiz:
                db.session.delete(ids)
            db.session.delete(chapter)
            db.session.commit()
    else:
        flash("Invalid input", "error")
    return redirect(url_for("admin"))

@app.route("/quiz/<action>", methods=["POST"])
@app.route("/quiz/<action>/<int:id>", methods=["POST"])
def quiz(action, id=None):
    if action == "add":
        db.session.add(Quiz(subject_id=request.form.get("subject"),
                            name=request.form.get("name"),
                            quiz_date=datetime.strptime(request.form.get("date"), r'%Y-%m-%d').date(),
                            time_duration=datetime.strptime(request.form.get("hour")+':'+request.form.get("minute"), r'%H:%M').time()))
        db.session.commit()
    elif action == "update":
        quiz = Quiz.query.filter_by(id=id).first()
        if quiz:
            quiz.name = request.form.get("name")
            quiz.quiz_date = datetime.strptime(request.form.get("date"), r'%Y-%m-%d').date(),
            quiz.time_duration = datetime.strptime(request.form.get("hour")+':'+request.form.get("minute"), r'%H:%M').time()
            db.session.commit()
    elif action == "delete":
        quiz = Quiz.query.filter_by(id=id).first()
        if quiz:
            for obj in Quizwisequestion.query.filter_by(quiz_id=id).all():
                db.session.delete(obj)
            db.session.delete(quiz)
            db.session.commit()
    else:
        flash("Invalid input", "error")
    return redirect(url_for("admin_quiz"))

@app.route("/quiz/question/<action>/<int:quiz_id>", methods=["POST"])
def add_question_to_quiz(action, quiz_id):
    question_id = request.form.get("question_id")
    if action == "append":
        if not Quizwisequestion.query.filter_by(quiz_id=quiz_id, question_id=question_id).first():
            db.session.add(Quizwisequestion(
                quiz_id=quiz_id,
                question_id=question_id
            ))
            db.session.commit()
        else:
            flash("Question already exist in quiz!", "error")
    elif action == "delete":
        question = Quizwisequestion.query.filter_by(question_id=question_id, quiz_id=quiz_id).first()
        if question:
            db.session.delete(question)
            db.session.commit()
    return redirect(url_for("admin_quiz"))

@app.route("/question/<action>", methods=["POST"])
@app.route("/question/<action>/<int:id>", methods=["POST"])
def question(action, id=None):
    if action == "add":
        db.session.add(Question(
            chapter_id=request.form.get("chapter_id"),
            title=request.form.get("title"),
            statement=request.form.get("statement"),
            option1=request.form.get("option1"),
            option2=request.form.get("option2"),
            option3=request.form.get("option3"),
            option4=request.form.get("option4"),
            correct_option=request.form.get("correct_option")))
        db.session.commit()
        return redirect(url_for("admin"))
    elif action == "update":
        question = Question.query.filter_by(id=id).first()
        question.title=request.form.get("title")
        question.statement=request.form.get("statement")
        question.option1=request.form.get("option1")
        question.option2=request.form.get("option2")
        question.option3=request.form.get("option3")
        question.option4=request.form.get("option4")
        question.correct_option=request.form.get("correct_option")
        db.session.commit()
        return redirect(url_for("admin"))
    elif action == "delete":
        question = Question.query.filter_by(id=id).first()
        quizwisequestions = Quizwisequestion.query.filter_by(question_id=id).all()
        if question:
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