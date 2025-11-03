from flask import Flask, render_template, request, redirect, url_for
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
    if request.method == "POST":
        task_id = request.form.get("task_id")
        task = request.form.get("task")
        status = request.form.get("status")
        priority = request.form.get("priority")
        due_date = request.form.get("due_date")
        if task_id:
            record = {"task_id": task_id, "task": task, "status": status, "priority": priority,
                      "due_date": due_date}
            add_data(record)
            print(read_data())
        return redirect(url_for("todo"))
    return render_template(template_name_or_list="todo.html")

@app.route("/habit.html")
def habit():
    return render_template("habit.html")

@app.route("/pomodoro.html")
def pomodoro():
    return render_template("pomodoro.html")

if __name__ == '__main__':
    app.run(debug=True)

