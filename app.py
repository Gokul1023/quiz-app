from flask import Flask, render_template, request, redirect, session
import pymysql

app = Flask(__name__)
app.secret_key = "secretkey"

# DB Connection
conn = pymysql.connect(
    host="127.0.0.1",
    user="root",
    password="Gokul@1023",
    database="quiz_app"
)

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form['username']
    password = request.form['password']

    cursor = conn.cursor()

    # Check existing user
    cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
    existing = cursor.fetchone()

    if existing:
        return "Username already exists"

    cursor.execute(
        "INSERT INTO users(username, password) VALUES(%s, %s)",
        (username, password)
    )
    conn.commit()

    return redirect("/login")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form['username']
    password = request.form['password']

    cursor = conn.cursor()
    cursor.execute(
        "SELECT id,username FROM users WHERE username=%s AND password=%s",
        (username, password)
    )
    user = cursor.fetchone()

    if user:
        session['user_id'] = user[0]
        session['username'] = user[1]
        return redirect("/")

    return "Invalid Login"


# QUIZ
@app.route("/")
def quiz():
    if 'user_id' not in session:
        return redirect("/login")

    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, question, option1, option2, option3, option4 FROM questions"
    )
    questions = cursor.fetchall()

    return render_template("quiz.html", questions=questions)


# SUBMIT
@app.route("/submit", methods=["POST"])
def submit():
    if 'user_id' not in session:
        return redirect("/login")

    cursor = conn.cursor()
    cursor.execute("SELECT id, answer FROM questions")
    correct_answers = cursor.fetchall()

    score = 0

    for q in correct_answers:
        qid = str(q[0])
        real_answer = q[1]
        user_answer = request.form.get(qid)

        if user_answer == real_answer:
            score += 1

    # Save result
    user_id = session['user_id']

    cursor.execute(
        "INSERT INTO results(user_id, score) VALUES(%s, %s)",
        (user_id, score)
    )
    conn.commit()

    return render_template("result.html", score=score)


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# RUN
if __name__ == "__main__":
    app.run(debug=True)
