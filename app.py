from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os
import json
import secrets
import uuid
from datetime import datetime
from csv_file_writer import add_data, read_data, update_data, delete_data
from due_date_comparison import compare_due_date  # ✅ fixed import

# ------------------ APP CONFIG ------------------
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# ------------------ BASE DIR & FILE PATHS ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

USER_FILE = os.path.join(BASE_DIR, "users.csv")
TODO_FOLDER = os.path.join(BASE_DIR, "user_todos")
CSV_FILE = os.path.join(BASE_DIR, "events.csv")
HABITS_FILE = os.path.join(BASE_DIR, "habits.json")
SESSIONS_FILE = os.path.join(BASE_DIR, "sessions.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

# ------------------ INITIAL SETUP ------------------
def init_files():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["username", "password"])
    if not os.path.exists(TODO_FOLDER):
        os.makedirs(TODO_FOLDER)
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "event_title", "event_time"])
    for file_path in [HABITS_FILE, SESSIONS_FILE, SETTINGS_FILE]:
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([] if "session" in file_path else {}, f, indent=4)

init_files()

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store"
    return response

# ------------------ USER HELPERS ------------------
def add_user(username, password):
    hashed_pw = generate_password_hash(password)
    with open(USER_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([username, hashed_pw])

def verify_user(username, password):
    if not os.path.exists(USER_FILE):
        return False
    with open(USER_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("username") == username and check_password_hash(row.get("password", ""), password):
                return True
    return False

def user_exists(username):
    if not os.path.exists(USER_FILE):
        return False
    with open(USER_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        return any(row.get("username") == username for row in reader)

def get_user_todo_file(username):
    return os.path.join(TODO_FOLDER, f"todo_task_data_{username}.csv")

# ------------------ AUTH ROUTES ------------------
@app.route("/")
def home():
    if "username" in session:
        return render_template("index.html", username=session["username"])
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not username or not password:
            flash("Please fill all fields.", "warning")
            return redirect(url_for("signup"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("signup"))
        if user_exists(username):
            flash("Username already exists.", "warning")
            return redirect(url_for("signup"))

        add_user(username, password)
        open(get_user_todo_file(username), "a", encoding="utf-8").close()
        flash("Signup successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
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

# ------------------ TODO ROUTES ------------------
@app.route("/todo")
def todo():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    filename = get_user_todo_file(username)

    # if os.path.exists(filename):
    #     try:
    #         compare_due_date(filename)
    #     except Exception:
    #         pass

    tasks = read_data(username)
    tasks = [{k: v.strip() if isinstance(v, str) else v for k, v in t.items()} for t in tasks]
    return render_template("todo.html", tasks=tasks, username=username)

@app.route("/get_todos", methods=["GET"])
def get_todos():
    if "username" not in session:
        return jsonify([])
    username = session["username"]
    tasks = read_data(username)
    tasks = [{k: v.strip() if isinstance(v, str) else v for k, v in t.items()} for t in tasks]
    return jsonify(tasks)

@app.route("/add_task", methods=["POST"])
def add_task():
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 403

    try:
        data = request.get_json()
        task_text = data.get("task", "").strip()
        status = data.get("status", "Pending").strip()
        priority = data.get("priority", "Low").strip()
        due_date = data.get("due_date", "").strip()

        if not task_text:
            return jsonify({"error": "Task cannot be empty."}), 400

        records = read_data(session["username"])
        record = {
            "task_id": str(len(records) + 1),
            "task": task_text,
            "status": status,
            "priority": priority,
            "due_date": due_date,
        }
        add_data(record, session["username"])
        return jsonify({"message": "✅ Task added successfully!"})
    except Exception as e:
        return jsonify({"error": f"Server error: {e}"}), 500


@app.route("/delete_task/<task_id>", methods=["POST"])
def delete_task(task_id):
    if "username" not in session:
        return jsonify({"error": "Not logged in"}), 403
    delete_data(task_id, session["username"])
    return jsonify({"message": "Task deleted"})

@app.route("/reviewmypriority", methods=["POST"])
def review_my_priority():
    if "username" not in session:
        return jsonify({"message": "❌ User not logged in."}), 403

    username = session["username"]
    filename = get_user_todo_file(username)

    if not os.path.exists(filename):
        return jsonify({"message": "❌ No tasks found for this user."}), 404

    try:
        updated = compare_due_date(filename)
        return jsonify({
            "message": f"✅ {len(updated)} tasks re-evaluated successfully!",
            "updated_tasks": updated
        })
    except Exception as e:
        return jsonify({"message": f"❌ Error: {e}"}), 500

# ------------------ CALENDAR ------------------
@app.route("/calendar")
def calendar():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("calendar.html")

@app.route("/api/events", methods=["GET", "POST", "DELETE"])
def handle_events():
    if request.method == "GET":
        if not os.path.exists(CSV_FILE):
            return jsonify({"success": True, "events": []})
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return jsonify({"success": True, "events": list(reader)})
    elif request.method == "POST":
        data = request.get_json()
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["date", "event_title", "event_time"])
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([data.get("date"), data.get("event_title"), data.get("event_time", "")])
        return jsonify({"success": True})
    elif request.method == "DELETE":
        data = request.get_json()
        date, title = data.get("date"), data.get("event_title")
        if not os.path.exists(CSV_FILE):
            return jsonify({"success": True})
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, ["date", "event_title", "event_time"])
            rows = [r for r in reader if not (len(r) >= 2 and r[0] == date and r[1] == title)]
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
        return jsonify({"success": True})

# ------------------ HABIT TRACKER ------------------
@app.route("/habit")
def habit():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("habit.html")

@app.route("/save_habits", methods=["POST"])
def save_habits():
    data = request.get_json()
    with open(HABITS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return jsonify({"message": "Saved!"})

@app.route("/get_habits", methods=["GET"])
def get_habits():
    if not os.path.exists(HABITS_FILE):
        return jsonify({})
    with open(HABITS_FILE, "r", encoding="utf-8") as f:
        try:
            return jsonify(json.load(f))
        except json.JSONDecodeError:
            return jsonify({})

# ------------------ POMODORO ------------------
@app.route("/pomodoro")
def pomodoro():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("pomodoro.html")

@app.route("/api/session", methods=["POST"])
def save_session():
    data = request.get_json()
    session_entry = {
        "type": data.get("type"),
        "cycle": data.get("cycle"),
        "duration": data.get("duration", 25),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if not os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(SESSIONS_FILE, "r+", encoding="utf-8") as f:
        try:
            sessions = json.load(f)
            if not isinstance(sessions, list):
                sessions = []
        except json.JSONDecodeError:
            sessions = []
        sessions.append(session_entry)
        f.seek(0)
        f.truncate()
        json.dump(sessions, f, indent=4)
    return jsonify({"message": "Session saved"})

@app.route("/api/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        data = request.get_json()
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return jsonify({"message": "Settings saved"})
    if not os.path.exists(SETTINGS_FILE):
        return jsonify({})
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        try:
            return jsonify(json.load(f))
        except json.JSONDecodeError:
            return jsonify({})

# ------------------ MAIN ------------------
if __name__ == "__main__":
    init_files()
    app.run(debug=True)
