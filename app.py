from flask import Flask, render_template, request, jsonify
import csv
import os
from datetime import datetime

app = Flask(__name__)

# Path to CSV file
CSV_FILE = 'events.csv'

# Initialize CSV file if it doesn't exist
def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'event_title', 'event_time'])

init_csv()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calendar')
def calendar():
    return render_template('calendar.html')
@app.route('/todo')
def todo_page():
    return render_template('todo.html')

@app.route('/habit')
def habit_page():
    return render_template('habit.html')

@app.route('/pomodoro')
def pomodoro_page():
    return render_template('pomodoro.html')

# Get all events
@app.route('/api/events', methods=['GET'])
def get_events():
    events = []
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                events.append(row)
        return jsonify({'success': True, 'events': events})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Add a new event
@app.route('/api/events', methods=['POST'])
def add_event():
    try:
        data = request.json
        date = data.get('date')
        event_title = data.get('event_title')
        event_time = data.get('event_time', '')
        
        if not date or not event_title:
            return jsonify({'success': False, 'error': 'Date and event title are required'})
        
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([date, event_title, event_time])
        
        return jsonify({'success': True, 'message': 'Event added successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Delete an event
@app.route('/api/events', methods=['DELETE'])
def delete_event():
    try:
        data = request.json
        date = data.get('date')
        event_title = data.get('event_title')
        
        # Read all events
        events = []
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if not (row[0] == date and row[1] == event_title):
                    events.append(row)
        
        # Write back without the deleted event
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(events)
        
        return jsonify({'success': True, 'message': 'Event deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)