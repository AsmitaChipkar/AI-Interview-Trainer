from flask import Flask, render_template, request, redirect, session
import sqlite3
import requests
import random
from werkzeug.security import generate_password_hash, check_password_hash
from llm_engine import evaluate_with_llm

app = Flask(__name__)
app.secret_key = "secretkey"

TOTAL_QUESTIONS = 5

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


questions_data = {

    "Python":[
        "What is a list in Python?",
        "Explain OOP in Python.",
        "What is a dictionary?",
        "What are decorators?",
        "Explain exception handling.",
        "What is lambda function?",
        "Difference between tuple and list?",
        "What are Python modules?",
        "Explain inheritance in Python.",
        "What is polymorphism?",
        "What is __init__ method?",
        "Explain file handling in Python.",
        "What is a set in Python?",
        "Difference between deep copy and shallow copy?",
        "What is recursion?",
        "What is a generator?",
        "What are *args and **kwargs?",
        "Explain Python packages.",
        "What is PEP8?",
        "How is memory managed in Python?"
    ],

    "Java":[
        "What is inheritance in Java?",
        "Explain polymorphism.",
        "What is JVM?",
        "Difference between interface and abstract class?",
        "What is encapsulation?",
        "What is constructor in Java?",
        "Explain method overloading.",
        "Explain method overriding.",
        "What is multithreading?",
        "What are access modifiers?",
        "What is exception handling in Java?",
        "What is the use of final keyword?",
        "Difference between ArrayList and LinkedList?",
        "What is garbage collection?",
        "Explain static keyword.",
        "What is package in Java?",
        "What is synchronization?",
        "Difference between == and equals()?",
        "Explain StringBuffer and StringBuilder.",
        "What is abstraction?"
    ],

    "C":[
        "What is a pointer?",
        "Explain malloc and calloc.",
        "What is structure in C?",
        "Difference between stack and heap?",
        "What is segmentation fault?",
        "What is function pointer?",
        "What is dynamic memory allocation?",
        "Explain arrays in C.",
        "Difference between call by value and call by reference?",
        "What is recursion in C?",
        "What is preprocessor directive?",
        "Explain header files.",
        "What is null pointer?",
        "What is dangling pointer?",
        "Difference between while and do while?",
        "What is union in C?",
        "Explain string handling functions.",
        "What is static variable?",
        "What is extern keyword?",
        "What is command line argument in C?"
    ],

    "HR":[
        "Tell me about yourself.",
        "What are your strengths?",
        "Why should we hire you?",
        "Describe a challenge you faced.",
        "Where do you see yourself in 5 years?",
        "Why do you want this job?",
        "Tell me about your weaknesses.",
        "How do you handle pressure?",
        "Describe your leadership experience.",
        "Why did you choose this career?",
        "How do you handle failure?",
        "What motivates you?",
        "Tell me about a team conflict.",
        "How do you manage deadlines?",
        "What makes you different from others?",
        "Why should we not hire you?",
        "Describe your ideal workplace.",
        "How do you learn new skills?",
        "Tell me about your biggest achievement.",
        "How do you prioritize tasks?"
    ]
}


def get_db():
    conn = sqlite3.connect("interview.db")
    conn.row_factory = sqlite3.Row
    return conn


def safe_num(value, default=0):
    try:
        return float(str(value).strip().replace("/10",""))
    except:
        return default


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("home.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        db = get_db()
        cur = db.cursor()

        try:
            cur.execute(
                "INSERT INTO users (username,password) VALUES (?,?)",
                (username,password)
            )
            db.commit()
            return redirect("/login")

        except:
            return "Username already exists"

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cur = db.cursor()

        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect("/dashboard")

        else:
            return "Invalid login"

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT category,score,date FROM interview_history WHERE user_id=?",
        (session["user_id"],)
    )

    raw_history = cur.fetchall()

    history = []
    for row in raw_history:
        history.append({
            "category": row["category"],
            "score": safe_num(row["score"]),
            "date": row["date"]
        })

    total_interviews = len(history)

    avg_score = round(
        sum([row["score"] for row in history]) / total_interviews,2
    ) if total_interviews else 0

    return render_template(
        "dashboard.html",
        history=history,
        total_interviews=total_interviews,
        avg_score=avg_score
    )


# ---------------- START PAGE ----------------
@app.route("/startpage")
def startpage():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("startpage.html")


# ---------------- INTERVIEW ----------------
@app.route("/interview", methods=["GET","POST"])
def interview():

    if "user_id" not in session:
        return redirect("/login")

    incoming_category = request.args.get("category")

    if request.method == "GET" and incoming_category is not None:

        if incoming_category not in questions_data:
            return "Invalid Interview Category"

        session["category"] = incoming_category
        session["q_index"] = 0
        session["answers"] = []
        session["questions"] = random.sample(questions_data[incoming_category], TOTAL_QUESTIONS)
        session.modified = True

    category = session.get("category")

    if not category:
        return redirect("/startpage")

    if request.method == "POST":

        answer = request.form.get("answer", "").strip()

        if answer == "":
            question = session["questions"][session["q_index"]]

            return render_template(
                "interview.html",
                question=question,
                qno=session["q_index"] + 1,
                total=TOTAL_QUESTIONS,
                category=category,
                error="Please enter your answer."
            )

        current_answers = session.get("answers", [])
        current_answers = current_answers + [answer]
        session["answers"] = current_answers

        session["q_index"] = session.get("q_index", 0) + 1
        session.modified = True

    if session["q_index"] >= TOTAL_QUESTIONS:

        answers_text = ""

        for i in range(TOTAL_QUESTIONS):
            q = session["questions"][i]
            a = session["answers"][i]
            answers_text += f"Question {i+1}: {q}\nAnswer: {a}\n\n"

        result = evaluate_with_llm(
            "Evaluate interview answers",
            answers_text
        )

        score = safe_num(result.get("overall_score", 6))

        db = get_db()
        cur = db.cursor()

        cur.execute(
            "INSERT INTO interview_history (user_id,category,score) VALUES (?,?,?)",
            (session["user_id"], category, score)
        )
        db.commit()

        session.pop("q_index", None)
        session.pop("questions", None)
        session.pop("answers", None)
        session.pop("category", None)
        session.modified = True

        return render_template(
            "result.html",
            score=score,
            strengths=result.get("strengths", ""),
            weaknesses=result.get("weaknesses", ""),
            improvements=result.get("improvements", "")
        )

    question = session["questions"][session["q_index"]]

    return render_template(
        "interview.html",
        question=question,
        qno=session["q_index"] + 1,
        total=TOTAL_QUESTIONS,
        category=category
    )


# ---------------- CHAT ----------------
@app.route("/chat", methods=["GET","POST"])
def chat():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        question = request.json.get("question")

        try:
            prompt = f"""
You are an AI interview assistant.

Rules:
- Give short and direct answers
- Keep answers crisp and clear
- Use 2-5 lines for normal questions
- Expand only if needed
- Avoid unnecessary explanation

Question:
{question}
"""

            r = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model":"phi3",
                    "prompt":prompt,
                    "stream":False
                }
            )

            response = r.json()["response"]

        except:
            response = "AI service unavailable."

        return {"answer":response}

    return render_template("chat.html")


# ---------------- HISTORY ----------------
@app.route("/history")
def history():

    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT category,score,date FROM interview_history WHERE user_id=? ORDER BY date DESC",
        (session["user_id"],)
    )

    raw = cur.fetchall()
    interviews = []

    for row in raw:
        interviews.append({
            "category": row["category"],
            "score": safe_num(row["score"]),
            "date": row["date"]
        })

    return render_template("history.html", interviews=interviews)


# ---------------- PROFILE ----------------
@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT score FROM interview_history WHERE user_id=? ORDER BY date DESC",
        (session["user_id"],)
    )

    rows = cur.fetchall()
    scores = [safe_num(row["score"]) for row in rows]

    total = len(scores)
    avg_score = round(sum(scores)/total,2) if total else 0
    best = max(scores) if scores else 0
    last = scores[0] if scores else 0

    if avg_score >= 8:
        level = "Advanced"
    elif avg_score >= 6:
        level = "Intermediate"
    else:
        level = "Beginner"

    achievements = []

    if total >= 1:
        achievements.append("Completed First Interview")
    if total >= 5:
        achievements.append("5 Interview Milestone")
    if best >= 8:
        achievements.append("High Scorer")
    if avg_score >= 7:
        achievements.append("Consistent Performer")

    return render_template(
        "profile.html",
        username=session["username"],
        total=total,
        avg=avg_score,
        best=best,
        last=last,
        level=level,
        achievements=achievements
    )


# ---------------- ADMIN SELECT ----------------
@app.route("/admin")
def admin_select():
    return render_template("admin_select.html")


# ---------------- ADMIN LOGIN ----------------
@app.route("/admin-login", methods=["GET","POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin-dashboard")

        else:
            return "Invalid admin credentials"

    return render_template("admin_login.html")


# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin-dashboard")
def admin_dashboard():

    if "admin" not in session:
        return redirect("/admin-login")

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM interview_history")
    total_interviews = cur.fetchone()[0]

    cur.execute("SELECT AVG(score) FROM interview_history")
    avg = cur.fetchone()[0]
    avg_score = round(safe_num(avg),2)

    cur.execute("SELECT category, COUNT(*) as c FROM interview_history GROUP BY category")
    category_data = cur.fetchall()

    cur.execute("""
    SELECT users.id, users.username,
    COUNT(interview_history.id) as interviews,
    AVG(interview_history.score) as avgscore
    FROM users
    LEFT JOIN interview_history ON users.id = interview_history.user_id
    GROUP BY users.id
    ORDER BY users.id DESC
    """)
    users_data = cur.fetchall()

    cur.execute("""
    SELECT users.username, interview_history.category, interview_history.score, interview_history.date
    FROM interview_history
    JOIN users ON users.id = interview_history.user_id
    ORDER BY interview_history.date DESC
    LIMIT 8
    """)
    recent_activity = cur.fetchall()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_interviews=total_interviews,
        avg_score=avg_score,
        category_data=category_data,
        users_data=users_data,
        recent_activity=recent_activity
    )


# ---------------- DELETE USER ----------------
@app.route("/delete-user/<int:user_id>")
def delete_user(user_id):

    if "admin" not in session:
        return redirect("/admin-login")

    db = get_db()
    cur = db.cursor()

    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    cur.execute("DELETE FROM interview_history WHERE user_id=?", (user_id,))
    db.commit()

    return redirect("/admin-dashboard")


# ---------------- ANALYTICS ----------------
@app.route("/analytics")
def analytics():

    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    cur = db.cursor()

    cur.execute("""
    SELECT category, AVG(score) as avg_score
    FROM interview_history
    WHERE user_id=?
    GROUP BY category
    """,(session["user_id"],))

    data = cur.fetchall()

    categories = [row["category"] for row in data]
    scores = [safe_num(row["avg_score"]) for row in data]

    return render_template(
        "analytics.html",
        categories=categories,
        scores=scores
    )


if __name__ == "__main__":
    app.run(debug=True)