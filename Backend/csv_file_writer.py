import csv
import os

def add_data(record):
    file_exists = os.path.isfile('todo_task_data.csv')

    with open('todo_task_data.csv', 'a', newline='') as f:
        fieldnames = ["task", "task_id", "status", "priority", "due_date"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        # Write header only once (when file is new)
        if not file_exists:
            writer.writeheader()

        writer.writerow(record)
