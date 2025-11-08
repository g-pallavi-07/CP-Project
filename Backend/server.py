from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os
import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # new random secret key per run

USER_FILE = "users.csv"
TODO_FOLDER = "user_todos"  # all user CSVs stored here

# ---------------------------------------------------
# Utility functions for user management
# ---------------------------------------------------

def create_user_file():
    """Create the user CSV if it doesn't exist."""
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["username", "password"])  # header


def add_user(username, password):
    """Add a new user with a hashed password."""
    hashed_pw = generate_password_hash(password)
    with open(USER_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([username, hashed_pw])


def verify_user(username, password):
    """Check if user exists and password is correct."""
    with open(USER_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username and check_password_hash(row["password"], password):
                return True
    return False


def user_exists(username):
    """Check if a username already exists."""
    with open(USER_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                return True
    return False


# ---------------------------------------------------
# Utility functions for To-Do management
# ---------------------------------------------------

def get_user_todo_file(username):
    """Return the CSV path for the user's To-Do list."""
    if not os.path.exists(TODO_FOLDER):
        os.makedirs(TODO_FOLDER)
    return os.path.join(TODO_FOLDER, f"todo_task_data_{username}.csv")


def create_user_todo_file(username):
    """Create a To-Do file for the user if not present."""
    file_path = get_user_todo_file(username)
    if not os.path.exists(file_path):
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["task_id", "task", "status", "priority", "due_date"])


def add_todo_record(username, record):
    """Append a new To-Do record for the user."""
    file_path = get_user_todo_file(username)
    with open(file_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["task_id", "task", "status", "priority", "due_date"])
        writer.writerow(record)


def read_todo_data(username):
    """Read all To-Do tasks for the given user."""
    file_path = get_user_todo_file(username)
    if not os.path.exists(file_path):
        create_user_todo_file(username)
        return []
    with open(file_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


# ---------------------------------------------------
# Routes
# ---------------------------------------------------

@app.route("/")
def home():
    if "username" in session:
        return render_template("index.html", username=session["username"])
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    create_user_file()
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        confirm_password = request.form.get("confirm_password").strip()

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("signup"))
        if user_exists(username):
            flash("Username already exists.", "warning")
            return redirect(url_for("signup"))

        add_user(username, password)
        create_user_todo_file(username)  # each new user gets an empty To-Do file
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    create_user_file()
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if verify_user(username, password):
            session["username"] = username
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/calendar.html")
def calendar():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("calendar.html")


@app.route("/todo.html", methods=["GET", "POST"])
def todo():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    create_user_todo_file(username)

    if request.method == "POST":
        task_id = request.form.get("task_id")
        task = request.form.get("task")
        status = request.form.get("status")
        priority = request.form.get("priority")
        due_date = request.form.get("due_date")

        if task_id and task:
            record = {
                "task_id": task_id,
                "task": task,
                "status": status,
                "priority": priority,
                "due_date": due_date,
            }
            add_todo_record(username, record)

        return redirect(url_for("todo"))

    tasks = read_todo_data(username)
    return render_template("todo.html", tasks=tasks)


@app.route("/reviewmypriority", methods=["POST"])
def review_my_priority():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user_file = get_user_todo_file(username)

    # Example: run due date comparison (user-specific)
    from due_date_comparison import compare_due_date
    compare_due_date(user_file)

    updated_records = read_todo_data(username)
    return jsonify(updated_records)


@app.route("/habit.html")
def habit():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("habit.html")


@app.route("/pomodoro.html")
def pomodoro():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("pomodoro.html")


if __name__ == "__main__":
    create_user_file()
    app.run(debug=True)
