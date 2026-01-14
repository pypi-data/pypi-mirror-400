# Reservation Calendar

This module allows you to create a week based calendar for your reservations.

For seasonal resorts, this module calculates week numbers and reservation dates based on a reference day (Memorial Day by default). The calendar is lightweight and uses pure Python with no external dependencies.

Inspired by Fun Valley Family Resort in South Fork, Colorado, USA.

## How it works

At Fun Valley guests are allowed to book "their" dates for the following year at checkout.  Since the resort is seasonal, opening on Memorial Day each year, the calendar slides forward and backward every 7th year.  Every 7th year there are 6 weeks in May.

If you stay in a cabin on June 9th, 2023 (Friday) thru June 11th, 2023 (Monday), you can book the same DAYS for the following year.  The calendar will show you the dates for the following year, June 7th, 2024 (Friday) thru June 10th, 2024 (Monday).

Since reservations are based on the day of the week in the given week of the season, the dates are calculated based on the day of the week of the current reservation.

## How to use it

```python
from reservation_calendar import ReservationCalendar

calendar = ReservationCalendar()

# Get week number and weekday number for a given date
date = datetime(2023, 6, 9)
week_number, weekday_number = calendar.get_week_info(date)
print("Week number:", week_number)
print("Weekday number:", weekday_number)

# Get day name for a given date
day_name = calendar.get_day_name(date)
print("Day name:", day_name)


print(f"Future Reservation Dates for {date}:")
for year in range(2024, 2035):
  print(f"{calendar.get_reservation_start_date(date, year)}")
```

### Output

```text
Week number: 2
Weekday number: 5
Day name: Friday
Future Reservation Dates for 2023-06-09:
2024-06-07
2025-06-06
2026-06-05
2027-06-11
2028-06-09
2029-06-08
2030-06-07
2031-06-06
2032-06-11
2033-06-10
2034-06-09
```
