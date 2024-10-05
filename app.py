# Flask --> Library (Pre-written Python code) which allows you to make web application using Python
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

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
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        command = "SELECT password FROM Users WHERE username = ?;"
        cursor.execute(command, (username,))
        result = cursor.fetchone()
        if result is None: # there is no user with the same username
            command = "INSERT INTO Users (username, password) VALUES (?,?);"
            cursor.execute(command, (username, password, ))
            conn.commit()
            conn.close()
            print("Successfully registered! ")
            return redirect(url_for('login'))
        else: # there is already user that has same username
            flash("Exisiting Username")
            return render_template('register.html')
    return render_template('register.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"] # scott
        password = request.form["password"] # 123 # password what user put in the login page
        conn = sqlite3.connect('database.db') # Connecting to DB
        cursor = conn.cursor()
        command = "SELECT password FROM Users WHERE username = ?;"
        cursor.execute(command, (username, ))
        password_db = cursor.fetchone() # The acutal password that is stored in our db
        if password_db is None: # when user tries to login with the username that have not registered yet.
            flash("Wrong username or password")
            return render_template('login.html')

        if password == password_db[0]: # when username and password are valid
            session["username"] = username
            return redirect(url_for('index'))
        else:
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

