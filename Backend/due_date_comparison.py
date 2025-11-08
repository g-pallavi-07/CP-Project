import datetime
from csv_file_writer import read_data, update_data

def compare_due_date():
    today = datetime.datetime.today()
    records = read_data()  # read fresh data each time

    for record in records:
        due_date = record['due_date']
        due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d")  # date format from HTML <input type="date">
        days_left = (due_date - today).days

        if days_left <= 1:
            record['priority'] = 'Urgent'
        elif days_left <= 2:
            record['priority'] = 'High'
        elif days_left <= 7:
            record['priority'] = 'Medium'
        else:
            record['priority'] = 'Low'

        update_data(record['task_id'], record)
