# Flask --> Library (Pre-written Python code) which allows you to make web application using Python
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "abc"

# sesssion = {}


# adding contents to our website
@app.route('/')
def index():
    isLogin = False # variable check whehter the user is loggined or not.
    if 'username' in session:
        isLogin = True
    return render_template('index.html', isLogin = isLogin)

@app.route('/register', methods = ["GET", "POST"])
def register():
    return render_template('register.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"] # scott
        password = request.form["password"] # 123
        if username == "test" and password == "123": # Valid username and password
            session["username"] = "test"
            return redirect(url_for('index'))
        else: # Invalid username and password
            flash("Wrong username or password")
            return render_template('login.html')

    else: # When user sends HTTP request with GET
        return render_template('login.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/task")
def task():
    isLogin = False
    if 'username' in session:
        isLogin = True
    return render_template('task.html', isLogin=isLogin)

# For running the web applications
if __name__ == '__main__':
    app.run(debug=True)

