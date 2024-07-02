from datetime import datetime, timedelta

# Get today's date
today = datetime.today()

# Calculate the last Monday
last_monday = today - timedelta(days=today.weekday())

# Calculate the first day of the current month
first_day_of_month = datetime(today.year, today.month, 1)

# Define date range
date_range_start = last_monday
date_range_end = today

print("Today:", today)
print("Last Monday:", last_monday)
print("First Day of the Month:", first_day_of_month)
print("Date Range Start:", date_range_start)
print("Date Range End:", date_range_end)
