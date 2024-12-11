from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pyrebase
from config import firebase_config
import random

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
    return render_template('index.html', isLogin=isLogin, show_navbar=True)

@app.route('/mindful', methods=['GET', 'POST'])
def mindful():
    isLogin = False
    if 'username' in session: # {"username" : "testtest"}
        isLogin = True
    if request.method == 'POST':
        # Handle user responses
        responses = request.form.to_dict()
        print("Mindful Responses:", responses)
        return redirect(url_for('study_process'))  # Redirect after submission
    return render_template('mindful.html',isLogin=isLogin, show_navbar=False)

@app.route('/non-mindful', methods=['GET', 'POST'])
def non_mindful():
    isLogin = False
    if 'username' in session: # {"username" : "testtest"}
        isLogin = True
    if request.method == 'POST':
        # Handle user responses
        responses = request.form.to_dict()
        print("Non-Mindful Responses:", responses)
        return redirect(url_for('index'))  # Redirect after submission
    return render_template('non_mindful.html',isLogin=isLogin, show_navbar=False)
@app.route('/study_process', methods=["GET", "POST"])
def study_process():
    isLogin = False
    if 'username' in session:
        isLogin = True
        user_id = session["username"].replace(".", "_").replace("@", "_")
        progress = db.child("users").child(user_id).child("study_progress").get().val() or {"current_step": 1}

        # Check task completion statuses
        task1_complete = db.child("users").child(user_id).child("game_result_task1").get().val() is not None
        task2_complete = db.child("users").child(user_id).child("game_result_task2").get().val() is not None
        task3_complete = db.child("users").child(user_id).child("game_result_task3").get().val() is not None





        if request.method == "POST":
            next_step = request.json.get("next_step")
            if next_step == 4:
                group = random.choice(["mindful", "non_mindful"])
                db.child("users").child(user_id).child("warmup_group").set(group)  # Save chosen group to Firebase
                db.child("users").child(user_id).child("study_progress").set({"current_step": int(next_step)})
                return jsonify({"status": "redirect", "url": url_for(group)})

            if next_step == 5:  # Step 4: Main Tasks
                # Redirect to the first incomplete task
                if not task1_complete:
                    return jsonify({"status": "redirect", "url": url_for("task")})
                elif not task2_complete:
                    return jsonify({"status": "redirect", "url": url_for("task2")})
                elif not task3_complete:
                    return jsonify({"status": "redirect", "url": url_for("task3")})
            elif next_step and int(next_step) > progress["current_step"]:
                db.child("users").child(user_id).child("study_progress").set({"current_step": int(next_step)})
            return jsonify({"status": "success", "current_step": int(next_step)})

    else:
        return redirect(url_for('login'))

    total_steps = 6  # Total number of steps in the process
    return render_template(
        "index2.html",
        isLogin=isLogin,
        current_step=progress["current_step"],
        total_steps=total_steps,
        steps=[
            {"step_number": 1, "title": "Informed Consent", "description": "Please review and provide consent.", "link": "#", "button_text": "Proceed"},
            {"step_number": 2, "title": "Pre-task Survey", "description": "Complete the pre-task survey.", "link": "https://www.jotform.com/build/243310688876063?iak=e9cfc2fe8d6c64782a898247fc0dc840-9725265b79d1c3af", "button_text": "Take Survey"},
            {"step_number": 3, "title": "Warm-up Activities", "description": "Engage in warm-up activities.", "link": "#", "button_text": "Start Warm-up"},
            {"step_number": 4, "title": "Main Tasks", "description": "Participate in the main study tasks.", "link": "#", "button_text": "Start Task"},
            {"step_number": 5, "title": "Post-task Surveys", "description": "Complete the post-task surveys.", "link": "https://www.jotform.com/build/243311500343440?iak=70ed55bf4126b2266b381045be46b770-70687ed665837d65", "button_text": "Take Survey"},
            {"step_number": 6, "title": "Debriefing", "description": "Read the debriefing information.", "link": "#", "button_text": "Finish"},
        ], show_navbar=True
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
    return render_template('task.html', isLogin=isLogin, show_navbar=False)


@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    if 'username' in session:
        responses = request.get_json()


        user_id = session["username"].replace(".", "_").replace("@", "_")

        db.child("users").child(user_id).child("survey_responses").set(responses)

        return jsonify({
            'status': 'success',
            'redirect_url': url_for('study_process')
        })
    else:
        return jsonify({'status': 'error', 'message': 'User not logged in'})


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
