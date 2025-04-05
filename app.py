import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, send_file
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'pidftc24670@gmail.com'  
app.config['MAIL_PASSWORD'] = 'PidWinHouston25!' 
app.config['MAIL_DEFAULT_SENDER'] = 'marvel551478@gmail.com'

mail = Mail(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///pid.db")
 
@app.route("/login", methods = ["GET", "POST"])
def login():
     # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        team_name = request.form.get("team_name")
        if not username:
            return apology("Type Username")

        elif not password:
            return apology("Type Password")

        elif not confirmation:
            return apology("Type Confirmation")
        
        elif not team_name:
            return apology("Type team name")

        elif password != confirmation:
            return apology("password don't Match")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) > 0:
            return apology("Username already exists")
        db.execute("INSERT INTO users (username, hash, team) VALUES (?, ?, ?)", username, generate_password_hash(password), team_name)

        rows1 = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        session["user_id"] = rows1[0]["id"]

        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/", methods=["GET", "POST"])
def index():
        return render_template("index.html")

@app.route("/usefulresources", methods=["GET", "POST"])
def usefulresources():
        return render_template("usefulresources.html")

@app.route("/3dmodels", methods=["GET", "POST"])
def models():
        return render_template("3dmodels.html")


@app.route("/pidpress", methods=["GET", "POST"])
def pidpress():
    categories = db.execute("SELECT DISTINCT category FROM news")

    # Get the selected category from the URL parameters (if any)
    selected_category = request.args.get('category', 'All')

    # Fetch news articles based on the selected category
    if selected_category == 'All':
        news_articles = db.execute("SELECT * FROM news")
    else:
        news_articles = db.execute("SELECT * FROM news WHERE category = ?", selected_category)

    return render_template('pidpress.html', news_articles=news_articles, categories=categories, selected_category=selected_category)



@app.route("/courses", methods=["GET", "POST"])
@login_required
def courses():
        courses = db.execute("SELECT * FROM courses")
        return render_template("courses.html", courses=courses)

@app.route("/aboutftc", methods=["GET", "POST"])
@login_required
def aboutftc():
        return render_template("aboutftc.html")

@app.route("/mycourses", methods=["GET", "POST"])
@login_required
def mycourses():
        if request.method == "POST":
            db.execute('UPDATE users SET courses = ""')
            return redirect("/mycourses")
        else:
            user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
            return render_template("mycourses.html", my=user)

@app.route("/courseofcading", methods=["GET", "POST"])
@login_required
def courseofcading():
        if request.method == "POST":
             user = session["user_id"]
             db.execute('UPDATE users SET courses = "Course of CADing" WHERE id = ?', user)
             return redirect("/courseofcading")
        else:
             user = session["user_id"]
             cad_db = db.execute('SELECT * FROM courses WHERE name = "Course of CADing"')
             user_cd = db.execute("SELECT * FROM users WHERE id = ?", user)
             return render_template("cad.html", cad=cad_db, user_cd=user_cd)
        
        return render_template("cad.html")

@app.route("/qa", methods=["GET", "POST"])
@login_required
def qa():
    if request.method == "POST":
        title = request.form.get("title").strip()
        body = request.form.get("body").strip()
        category = request.form.get("category")
        user_id = session["user_id"]

        # Validate input
        if not title:
            flash("Please enter a title for your question.", "danger")
        elif not body:
            flash("Please describe your question in the body field.", "danger")
        elif not category:
            flash("Please select a category.", "danger")
        else:
            db.execute("INSERT INTO questions (user_id, title, body, category) VALUES (?, ?, ?, ?)",
                       user_id, title, body, category)
            flash("Your question has been posted!", "success")
            return redirect("/qa")

    # Handle GET and also reload on POST failure
    selected_category = request.args.get("category", "All")
    categories = db.execute("SELECT DISTINCT category FROM questions")

    if selected_category == "All":
        questions = db.execute(
            "SELECT questions.*, users.username FROM questions JOIN users ON users.id = questions.user_id ORDER BY created_at DESC")
    else:
        questions = db.execute(
            "SELECT questions.*, users.username FROM questions JOIN users ON users.id = questions.user_id WHERE category = ? ORDER BY created_at DESC", selected_category)

    return render_template("qa.html", questions=questions, categories=categories, selected_category=selected_category)



@app.route("/qa/<int:question_id>", methods=["GET", "POST"])
@login_required
def question_detail(question_id):
    if request.method == "POST":
        answer = request.form.get("answer")
        if not answer:
            flash("Answer cannot be empty", "danger")
        else:
            db.execute("INSERT INTO answers (question_id, user_id, body) VALUES (?, ?, ?)",
                       question_id, session["user_id"], answer)
            flash("Answer submitted!", "success")
        return redirect(f"/qa/{question_id}")

    question = db.execute("SELECT questions.*, users.username FROM questions JOIN users ON users.id = questions.user_id WHERE questions.id = ?", question_id)
    if not question:
        return apology("Question not found")

    answers = db.execute("SELECT answers.*, users.username FROM answers JOIN users ON users.id = answers.user_id WHERE question_id = ? ORDER BY created_at ASC", question_id)

    return render_template("question_detail.html", question=question[0], answers=answers)

@app.route("/lesson1ofcad", methods=["GET", "POST"])
@login_required
def lesson1ofcading():
        lesson1ofcad_db = db.execute('SELECT * FROM lessons WHERE id = 1')
        return render_template("lesson1ofcad.html", lesson1cad=lesson1ofcad_db)

@app.route("/lesson2ofcad", methods=["GET", "POST"])
@login_required
def lesson2ofcading():
        lesson2ofcad_db = db.execute('SELECT * FROM lessons WHERE id = 2')
        return render_template("lesson2ofcad.html", lesson2cad=lesson2ofcad_db)

@app.route("/lesson3ofcad", methods=["GET", "POST"])
@login_required
def lesson3ofcading():
        lesson3ofcad_db = db.execute('SELECT * FROM lessons WHERE id = 3')
        return render_template("lesson3ofcad.html", lesson3cad=lesson3ofcad_db)

@app.route("/lesson4ofcad", methods=["GET", "POST"])
@login_required
def lesson4ofcading():
        lesson4ofcad_db = db.execute('SELECT * FROM lessons WHERE id = 4')
        return render_template("lesson3ofcad.html", lesson4cad=lesson4ofcad_db)