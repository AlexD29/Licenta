from datetime import datetime

published_date_str = "2024-05-03 10:27:49"
published_date = datetime.strptime(published_date_str, '%Y-%m-%d %H:%M:%S')

print(published_date)
