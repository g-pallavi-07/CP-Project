from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os
import json
import secrets
import base64
from datetime import datetime
from csv_file_writer import add_data, read_data, update_data, delete_data

# ------------------ APP CONFIG ------------------
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# ------------------ FILE PATHS ------------------
USER_FILE = "users.csv"
TODO_FOLDER = "user_todos"
CSV_FILE = "events.csv"
HABITS_FILE = "habits.json"
SESSIONS_FILE = "sessions.json"
SETTINGS_FILE = "settings.json"
UPLOAD_FOLDER = "static/profile_photos"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

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
    with open(USER_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username and check_password_hash(row["password"], password):
                return True
    return False

def user_exists(username):
    with open(USER_FILE, "r") as f:
        reader = csv.DictReader(f)
        return any(row["username"] == username for row in reader)

def get_user_todo_file(username):
    return os.path.join(TODO_FOLDER, f"todo_task_data_{username}.csv")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def update_user_password(username, new_password):
    """Update user password in CSV"""
    users = []
    updated = False
    
    with open(USER_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                row["password"] = generate_password_hash(new_password)
                updated = True
            users.append(row)
    
    if updated:
        with open(USER_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["username", "password"])
            writer.writeheader()
            writer.writerows(users)
    
    return updated

def update_username(old_username, new_username):
    """Update username in CSV and rename todo file"""
    users = []
    updated = False
    
    # Check if new username already exists
    if old_username != new_username and user_exists(new_username):
        return False
    
    with open(USER_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == old_username:
                row["username"] = new_username
                updated = True
            users.append(row)
    
    if updated:
        with open(USER_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["username", "password"])
            writer.writeheader()
            writer.writerows(users)
        
        # Rename todo file if it exists
        old_todo_file = get_user_todo_file(old_username)
        new_todo_file = get_user_todo_file(new_username)
        if os.path.exists(old_todo_file):
            os.rename(old_todo_file, new_todo_file)
        
        # Rename profile photo if it exists
        old_photo = os.path.join(UPLOAD_FOLDER, f"{old_username}_profile.jpg")
        new_photo = os.path.join(UPLOAD_FOLDER, f"{new_username}_profile.jpg")
        if os.path.exists(old_photo):
            os.rename(old_photo, new_photo)
    
    return updated

def save_profile_photo(username, photo_data):
    """Save base64 profile photo"""
    try:
        # Remove data URL prefix if present
        if ',' in photo_data:
            photo_data = photo_data.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(photo_data)
        
        # Save file
        filename = f"{username}_profile.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        return filename
    except Exception as e:
        print(f"Error saving profile photo: {e}")
        return None

def get_profile_photo_path(username):
    """Get profile photo path if exists"""
    filename = f"{username}_profile.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return f"/static/profile_photos/{filename}"
    return None

# ------------------ AUTH ROUTES ------------------
@app.route("/")
def home():
    if "username" in session:
        username = session["username"]
        photo_path = get_profile_photo_path(username)
        return render_template("index.html", username=username, profile_photo=photo_path)
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
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

# ------------------ PROFILE UPDATE ROUTE ------------------
@app.route("/update_profile", methods=["POST"])
def update_profile():
    """Handle profile updates"""
    if "username" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    
    current_username = session["username"]
    new_username = request.form.get("username", "").strip()
    current_password = request.form.get("current_password", "").strip()
    new_password = request.form.get("new_password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()
    profile_photo = request.form.get("profile_photo", "")
    
    changes_made = False
    
    # Validate username
    if not new_username:
        flash("Username cannot be empty.", "danger")
        return redirect(url_for("home"))
    
    if len(new_username) < 3:
        flash("Username must be at least 3 characters long.", "danger")
        return redirect(url_for("home"))
    
    # Update username if changed
    if new_username != current_username:
        if user_exists(new_username):
            flash("Username already exists. Please choose another.", "warning")
            return redirect(url_for("home"))
        
        if update_username(current_username, new_username):
            session["username"] = new_username
            current_username = new_username
            changes_made = True
        else:
            flash("Failed to update username.", "danger")
            return redirect(url_for("home"))
    
    # Update password if provided
    if new_password or confirm_password:
        if not current_password:
            flash("Please enter your current password to change it.", "danger")
            return redirect(url_for("home"))
        
        # Verify current password
        if not verify_user(current_username, current_password):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for("home"))
        
        if new_password != confirm_password:
            flash("New passwords do not match.", "danger")
            return redirect(url_for("home"))
        
        if len(new_password) < 6:
            flash("New password must be at least 6 characters long.", "danger")
            return redirect(url_for("home"))
        
        if update_user_password(current_username, new_password):
            changes_made = True
        else:
            flash("Failed to update password.", "danger")
            return redirect(url_for("home"))
    
    # Update profile photo if provided
    # In your Flask app.py, update the save_profile_photo function:

def save_profile_photo(username, photo_data):
    """Save base64 profile photo (now supports up to 15MB)"""
    try:
        # Remove data URL prefix if present
        if ',' in photo_data:
            photo_data = photo_data.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(photo_data)
        
        # Check file size (15MB max)
        max_size = 15 * 1024 * 1024  # 15MB
        if len(image_data) > max_size:
            return None
        
        # Save file
        filename = f"{username}_profile.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        return filename
    except Exception as e:
        print(f"Error saving profile photo: {e}")
        return None
    
    # Show appropriate message
    if changes_made:
        flash("Profile updated successfully!", "success")
    else:
        flash("No changes were made.", "info")
    
    return redirect(url_for("home"))

# ------------------ TODO ROUTES ------------------
@app.route("/todo")
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

    if not data or not data.get("task"):
        return jsonify({"error": "Task missing"}), 400

    records = read_data(username)
    record = {
        "task_id": str(len(records) + 1),
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
        with open(filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            tasks = list(reader)
        if not tasks:
            return jsonify({"message": "❌ No tasks to review."}), 404
        priority_order = {"Urgent": 1, "High": 2, "Medium": 3, "Low": 4}
        tasks.sort(key=lambda x: priority_order.get(x.get("priority", "Low"), 5))
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["task_id", "task", "status", "priority", "due_date"])
            writer.writeheader()
            for i, task in enumerate(tasks, start=1):
                task["task_id"] = str(i)
                writer.writerow(task)
        return jsonify({"message": "✅ Tasks reordered by priority successfully!"}), 200
    except Exception as e:
        return jsonify({"message": f"❌ Error: {e}"}), 500

# ------------------ CALENDAR ROUTES ------------------
@app.route("/calendar")
def calendar():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("calendar.html")

@app.route("/api/events", methods=["GET", "POST", "DELETE"])
def handle_events():
    if request.method == "GET":
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return jsonify({"success": True, "events": list(reader)})
    elif request.method == "POST":
        data = request.get_json()
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([data.get("date"), data.get("event_title"), data.get("event_time", "")])
        return jsonify({"success": True})
    elif request.method == "DELETE":
        data = request.get_json()
        date, title = data.get("date"), data.get("event_title")
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = [r for r in reader if not (r[0] == date and r[1] == title)]
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
    with open(HABITS_FILE, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))

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
    with open(SESSIONS_FILE, "r+") as f:
        try:
            sessions = json.load(f)
        except json.JSONDecodeError:
            sessions = []
        sessions.append(session_entry)
        f.seek(0)
        json.dump(sessions, f, indent=4)
    return jsonify({"message": "Session saved"})

@app.route("/api/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        data = request.get_json()
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f, indent=4)
        return jsonify({"message": "Settings saved"})
    with open(SETTINGS_FILE, "r") as f:
        return jsonify(json.load(f))

# ------------------ MAIN ------------------
if __name__ == "__main__":
    init_files()
    app.run(debug=True)