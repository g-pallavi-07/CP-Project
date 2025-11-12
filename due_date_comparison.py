import datetime
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def compare_due_date(user_file):
    if not os.path.isabs(user_file):
        user_file = os.path.join(BASE_DIR, user_file)

    if not os.path.isfile(user_file):
        return []

    today = datetime.datetime.today()
    updated_records = []

    try:
        with open(user_file, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for record in reader:
                if not record.get("due_date"):
                    continue
                try:
                    due_date = datetime.datetime.strptime(record["due_date"], "%Y-%m-%d")
                    days_left = (due_date - today).days
                except ValueError:
                    continue

                if days_left < 0 and record["status"].lower() != "completed":
                    record["priority"] = "Overdue"
                elif days_left <= 1:
                    record["priority"] = "Urgent"
                elif days_left <= 2:
                    record["priority"] = "High"
                elif days_left <= 7:
                    record["priority"] = "Medium"
                else:
                    record["priority"] = "Low"

                updated_records.append(record)

        with open(user_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["task_id", "task", "status", "priority", "due_date"])
            writer.writeheader()
            writer.writerows(updated_records)

        return updated_records

    except Exception as e:
        print(f"[Error] compare_due_date() failed: {e}")
        return []
