from flask import Flask, render_template, jsonify, request
from datetime import datetime

app = Flask(__name__)

sessions = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/pomodoro')
def pomodoro():
    return render_template('pomodoro.html')

@app.route('/api/session', methods=['POST'])
def save_session():
    data = request.get_json()
    sessions.append({
        "type": data.get("type"),
        "cycle": data.get("cycle"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return jsonify({"message": "Session saved", "sessions": sessions})

if __name__ == "__main__":
    app.run(debug=True)
