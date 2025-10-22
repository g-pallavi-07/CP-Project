from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route("/calendar.html")
def calendar():
    return render_template("calendar.html")

tasks = []

@app.route("/todo.html", methods=["GET", "POST"])
def todo():
    if request.method == "POST":
        task = request.form.get("task")
        if task:
            tasks.append({"task": task, "done": False})
            print(tasks)
        return redirect(url_for("todo"))
    return render_template("todo.html", tasks=tasks)

@app.route("/habit.html")
def habit():
    return render_template("habit.html")

@app.route("/pomodoro.html")
def pomodoro():
    return render_template("pomodoro.html")

if __name__ == '__main__':
    app.run(debug=True)

