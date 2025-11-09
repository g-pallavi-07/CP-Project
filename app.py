from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json

app = Flask(__name__)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route("/habit")
def habit_page():
    return render_template("habit.html")

@app.route("/save_habits", methods=["POST"])
def save_habits():
    data = request.json
    with open("habits.json", "w") as f:
        json.dump(data, f)
    return jsonify({"message": "Saved!"})

@app.route("/get_habits", methods=["GET"])
def get_habits():
    try:
        with open("habits.json", "r") as f:
            return jsonify(json.load(f))
    except:
        return jsonify([])

if __name__ == "__main__":
    app.run(debug=True)

