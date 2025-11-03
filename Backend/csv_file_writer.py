import csv
import os

FILE_NAME = 'todo_task_data.csv'
FIELDNAMES = ["task_id","task", "status", "priority", "due_date"]


def add_data(record):
    file_exists = os.path.isfile(FILE_NAME)
    with open(FILE_NAME, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader() # only writes header if file doesnt exist
        writer.writerow(record)


def read_data():
    records = []
    try:
        with open(FILE_NAME, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
    except FileNotFoundError:
        return []
    return records


def update_data(task_id, updated_record):
    records = read_data()
    updated = False

    for record in records:
        if record["task_id"] == str(task_id):
            record.update(updated_record)
            updated = True

    if updated:
        with open(FILE_NAME, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(records)
        print(f"✅ Task {task_id} updated successfully.")
    else:
        print(f"⚠️ Task ID {task_id} not found.")


def delete_data(task_id):
    records = read_data()
    new_records = []
    for record in records:
        if record["task_id"] != str(task_id):
            new_records.append(record)

    if len(new_records) == len(records):
        print(f"⚠️ Task ID {task_id} not found.")
    else:
        with open(FILE_NAME, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(new_records)
        print(f"🗑️ Task {task_id} deleted successfully.")
