from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os
import secrets
from csv_file_writer import add_data, read_data, update_data, delete_data

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

USER_FILE = "users.csv"
TODO_FOLDER = "user_todos"


# ------------------ USER HELPERS ------------------

def create_user_file():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["username", "password"])


def add_user(username, password):
    hashed_pw = generate_password_hash(password)
    with open(USER_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([username, hashed_pw])


def verify_user(username, password):
    with open(USER_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username and check_password_hash(row["password"], password):
                return True
    return False


def user_exists(username):
    with open(USER_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                return True
    return False


# ------------------ TO-DO HELPERS ------------------

def ensure_todo_folder():
    if not os.path.exists(TODO_FOLDER):
        os.makedirs(TODO_FOLDER)


def get_user_todo_file(username):
    ensure_todo_folder()
    return os.path.join(TODO_FOLDER, f"todo_task_data_{username}.csv")


# ------------------ ROUTES ------------------

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
        open(get_user_todo_file(username), "a").close()
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


# ------------------ TO-DO PAGE ------------------

@app.route("/todo.html")
def todo():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    tasks = read_data(username)
    return render_template("todo.html", tasks=tasks, username=username)


@app.route("/add_task", methods=["POST"])
def add_task():
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 403

    username = session["username"]
    data = request.get_json()

    records = read_data(username)
    task_id = len(records) + 1

    record = {
        "task_id": str(task_id),
        "task": data.get("task", ""),
        "status": data.get("status", "Pending"),
        "priority": data.get("priority", "Low"),
        "due_date": data.get("due_date", "")
    }

    add_data(record, username)
    return jsonify({"message": "✅ Task added successfully!"})


@app.route("/delete_task/<task_id>", methods=["POST"])
def delete_task(task_id):
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 403

    username = session["username"]
    delete_data(task_id, username)
    return jsonify({"message": "Task deleted"})


@app.route("/reviewmypriority", methods=["POST"])
def review_my_priority():
    import csv

    if "username" not in session:
        return jsonify({"message": "❌ User not logged in."}), 403

    username = session["username"]
    filename = os.path.join("user_todos", f"todo_task_data_{username}.csv")

    if not os.path.exists(filename):
        return jsonify({"message": "❌ No tasks found for this user."}), 404

    try:
        # Read all tasks
        with open(filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            tasks = list(reader)

        if not tasks:
            return jsonify({"message": "❌ No tasks to review."}), 404

        # Priority order
        priority_order = {"Urgent": 1, "High": 2, "Medium": 3, "Low": 4}

        # Sort tasks by priority
        tasks.sort(key=lambda x: priority_order.get(x.get("priority", "Low"), 5))

        # Rewrite file with updated order and new IDs
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["task_id", "task", "status", "priority", "due_date"])
            writer.writeheader()
            for i, task in enumerate(tasks, start=1):
                task["task_id"] = str(i)
                writer.writerow(task)

        return jsonify({"message": "✅ Tasks reordered by priority successfully!"}), 200

    except Exception as e:
        print("⚠️ Error while reviewing priority:", e)
        return jsonify({"message": f"❌ Error: {e}"}), 500



# ------------------ OTHER PAGES ------------------

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


# ------------------ MAIN ------------------

if __name__ == "__main__":
    create_user_file()
    ensure_todo_folder()
    app.run(debug=True)
