from flask import Flask, render_template, request, redirect, url_for, jsonify
from csv_file_writer import *
import datetime

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route("/calendar.html")
def calendar():
    return render_template("calendar.html")


@app.route("/todo.html", methods=["GET", "POST"])
def todo():
    from csv_file_writer import add_data, read_data

    if request.method == "POST":
        task_id = request.form.get("task_id")
        task = request.form.get("task")
        status = request.form.get("status")
        priority = request.form.get("priority")
        due_date = request.form.get("due_date")

        if task_id:
            record = {
                "task_id": task_id,
                "task": task,
                "status": status,
                "priority": priority,
                "due_date": due_date
            }
            add_data(record)

        # redirect to GET view to show updated list
        return redirect(url_for("todo"))

    # when GET request → show all tasks
    tasks = read_data()
    return render_template("todo.html", tasks=tasks)


@app.route("/reviewmypriority", methods=["POST"])
def review_my_priority():
    import csv
    from due_date_comparison import compare_due_date

    # Step 1: Run comparison to update priorities
    compare_due_date()

    # Step 2: Read updated CSV data
    updated_records = []
    with open('todo_task_data.csv', 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            updated_records.append(row)

    # Step 3: Return the updated tasks as JSON
    return jsonify(updated_records)


@app.route("/habit.html")
def habit():
    return render_template("habit.html")

@app.route("/pomodoro.html")
def pomodoro():
    return render_template("pomodoro.html")

if __name__ == '__main__':
    app.run(debug=True)

