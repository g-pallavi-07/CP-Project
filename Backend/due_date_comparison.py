import datetime
import csv

def compare_due_date(user_file):
    """Compare due dates and update priority for each record in the user's CSV."""
    today = datetime.datetime.today()
    updated_records = []

    with open(user_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for record in reader:
            if not record.get('due_date'):
                continue

            try:
                due_date = datetime.datetime.strptime(record['due_date'], "%Y-%m-%d")
                days_left = (due_date - today).days
            except ValueError:
                continue

            # ✅ NEW: Handle overdue tasks
            if days_left < 0 and record['status'].lower() != 'completed':
                record['priority'] = 'Overdue'
            elif days_left <= 1:
                record['priority'] = 'Urgent'
            elif days_left <= 2:
                record['priority'] = 'High'
            elif days_left <= 7:
                record['priority'] = 'Medium'
            else:
                record['priority'] = 'Low'

            updated_records.append(record)

    with open(user_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["task_id", "task", "status", "priority", "due_date"])
        writer.writeheader()
        writer.writerows(updated_records)

    return updated_records
