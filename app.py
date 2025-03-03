from flask import Flask, render_template, request,url_for,redirect,session
import sqlite3
app = Flask(__name__)

app.secret_key = 'erfgnjk-nvcfg'

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"
    
questions = [
    {
        "question": "I make important decisions based on:",
        "options": {
            "Kinesthetic": "the right gut level feelings.",
            "Auditory": "which way sounds the best and resonates for you",
            "Visual": "what looks best to me after clearly seeing the issues",
            "Read/Write": "precise review and study of the issues"
        }
    },
    {
        "question": "During an argument, I am most likely to be influenced by:",
        "options": {
            "Kinesthetic": "whether or not I am in touch with the other person's feelings",
            "Auditory": "the loudness or softness of the other person's tone of voice",
            "Visual": "whether or not I can see the other person's point of view",
            "Read/Write": "the logic of the other person's argument"
        }
    },
    {
        "question": "I mostly like to be aware of the following in conversation:",
        "options": {
            "Kinesthetic": "the beautiful feelings they and I share",
            "Auditory": "the sounds and intonations that come from the lovely tone of voice",
            "Visual": "the way people hold themselves and interesting facial expressions",
            "Read/Write": "the words I and they choose and whether it all makes good sense"
        }
    },
    {
        "question": "If I had the choice of these in order, first I would like to:",
        "options": {
            "Kinesthetic": "select the most comfortable furniture",
            "Auditory": "find the ideal volume and tuning on a stereo system",
            "Visual": "look around and take in the décor, pictures and how the room looks before do anything else.",
            "Read/Write": "select the most intellectually relevant point in an interesting subject"
        }
    },
    {
        "question": "Which describes your room that you live in:",
        "options": {
            "Kinesthetic": "The feel of the place is the most important to you",
            "Auditory": "The hi-fi is very prominent and you have an excellent collection",
            "Visual": "The colours you choose and the way a room looks are most important",
            "Read/Write": "It's a practical layout and things are situated in an excellent location"
        }
    }
]

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session['user_name'] = request.form.get("name")
        session['email'] = request.form.get("email")
        return redirect(url_for('quiz'))
    return render_template("index.html")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    user_name = session.get('user_name')
    email = session.get("email")

    if request.method == "POST":
        user_answers = {}
        for key, value in request.form.items():
            q_num, category = key.split("_")
            q_num = int(q_num[1:])
            if q_num not in user_answers:
                user_answers[q_num] = {}
            user_answers[q_num][category] = int(value)
        vark_scores = calculate_vark_scores(user_answers)
        dominant_style = max(vark_scores, key=vark_scores.get)

        store_results(user_name, email, vark_scores,dominant_style)
        return render_template("result.html", dominant_style=dominant_style, vark_scores=vark_scores)

    return render_template("quiz.html", questions=questions)

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("username") == ADMIN_USERNAME and request.form.get("password") == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard")) 
        return "Invalid credentials! Please try again."

    return render_template("admin_login.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM STUDENTS")
        students = cursor.fetchall()

    return render_template("admin.html", students=students)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



def calculate_vark_scores(user_answers):
    vark_scores = {"Visual": 0, "Auditory": 0, "Read/Write": 0, "Kinesthetic": 0}
    for question_num, rankings in user_answers.items():
        for category, rank in rankings.items():
            vark_scores[category] += int(rank)
    return vark_scores

def determine_dominant_style(vark_scores):
    dominant_style = max(vark_scores, key=vark_scores.get)
    return dominant_style

def create_database():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS STUDENTS(
                user_name TEXT ,
                email TEXT PRIMARY KEY,
                visual INTEGER DEFAULT 0,
                auditory INTEGER DEFAULT 0,
                read_write INTEGER DEFAULT 0,
                kinesthetic INTEGER DEFAULT 0,
                dominant_style TEXT
            )
        """)
        conn.commit()

def store_results(user_name, email, vark_scores,dominant_style):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO STUDENTS (user_name, email, visual, auditory, read_write, kinesthetic,dominant_style)
            VALUES (?, ?, ?, ?, ?, ?,?)
            ON CONFLICT(email) DO UPDATE SET 
                user_name=excluded.user_name, 
                visual=excluded.visual, 
                auditory=excluded.auditory, 
                read_write=excluded.read_write, 
                kinesthetic=excluded.kinesthetic,
                dominant_style=excluded.dominant_style
        """, (user_name, email, vark_scores["Visual"], vark_scores["Auditory"], vark_scores["Read/Write"], vark_scores["Kinesthetic"],dominant_style))
        conn.commit()


if __name__ == "__main__":
    create_database()  
    app.run(debug=True)

