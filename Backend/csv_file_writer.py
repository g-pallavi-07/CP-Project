import csv
import os

FIELDNAMES = ["task_id", "task", "status", "priority", "due_date"]


def get_filename(username):
    folder = "user_todos"
    if not os.path.exists(folder):
        os.makedirs(folder)
    return os.path.join(folder, f"todo_task_data_{username}.csv")


def add_data(record, username):
    filename = get_filename(username)
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)


def read_data(username):
    filename = get_filename(username)
    if not os.path.isfile(filename):
        return []
    with open(filename, "r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def update_data(task_id, updated_record, username):
    filename = get_filename(username)
    records = read_data(username)
    for record in records:
        if record["task_id"] == task_id:
            record.update(updated_record)
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)


def delete_data(task_id, username):
    filename = get_filename(username)
    records = read_data(username)
    new_records = [r for r in records if r["task_id"] != task_id]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(new_records)
