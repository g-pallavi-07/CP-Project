import datetime
from csv_file_writer import read_data, update_data

today = datetime.datetime.today()
records = read_data()

def compare_due_date():
    for record in records:
        due_date = record['due_date']
        due_date = datetime.datetime.strptime(due_date, "%d-%m-%Y")
        days_left = (due_date-today).days

        if days_left <= 1:
            record['priority'] = 'urgent'
        elif days_left <= 2:
            record['priority'] = 'high'
        elif days_left <= 7:
            record['priority'] = 'medium'
        elif days_left >7:
            record['priority'] = 'low'
        update_data(record['task_id'],record)

compare_due_date()