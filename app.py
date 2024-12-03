from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pyrebase
from config import firebase_config

app = Flask(__name__)
app.secret_key = "abc"

# Firebase configuration
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()


# Routes
@app.route('/')
def index():
    isLogin = 'username' in session
    return render_template('index.html', isLogin=isLogin)


@app.route('/study_process', methods=["GET", "POST"])
def study_process():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_id = session["username"].replace(".", "_").replace("@", "_")

    if request.method == "POST":
        next_step = request.json.get("next_step")
        db.child("users").child(user_id).update({"current_step": int(next_step)})
        return jsonify({"status": "success", "current_step": int(next_step)})

    # Fetch user progress
    user_data = db.child("users").child(user_id).get().val() or {}
    current_step = user_data.get("current_step", 1)

    # Render study process page
    total_steps = 6
    steps = [
        {"step_number": 1, "title": "Informed Consent", "description": "Please review and provide consent.",
         "link": "#", "button_text": "Proceed"},
        {"step_number": 2, "title": "Pre-task Survey", "description": "Complete the pre-task survey.",
         "link": "https://www.jotform.com/build/243311350088449", "button_text": "Take Survey"},
        {"step_number": 3, "title": "Warm-up Activities", "description": "Engage in warm-up activities.",
         "link": "#", "button_text": "Start Warm-up"},
        {"step_number": 4, "title": "Main Tasks", "description": "Participate in the main study tasks.",
         "link": "/task", "button_text": "Start Task"},
        {"step_number": 5, "title": "Post-task Surveys", "description": "Complete the post-task surveys.",
         "link": "https://www.jotform.com/build/243311949113452", "button_text": "Take Survey"},
        {"step_number": 6, "title": "Debriefing", "description": "Read the debriefing information.",
         "link": "#", "button_text": "Finish"},
    ]

    return render_template(
        "index2.html",
        isLogin=True,
        current_step=current_step,
        total_steps=total_steps,
        steps=steps
    )


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user_data = db.child("users").child(username.replace(".", "_").replace("@", "_")).get().val()

        if user_data is None:
            db.child("users").child(username.replace(".", "_").replace("@", "_")).set({"password": password})
            flash("Successfully registered!")
            return redirect(url_for('login'))
        else:
            flash("Existing Username")
    return render_template('register.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_data = db.child("users").child(username.replace(".", "_").replace("@", "_")).get().val()

        if user_data and user_data["password"] == password:
            session["username"] = username
            return redirect(url_for('index'))
        else:
            flash("Wrong username or password")
    return render_template('login.html')


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route("/task")
def task():
    isLogin = 'username' in session
    return render_template('task.html', isLogin=isLogin)


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
