from datetime import datetime
import pytest
from reservation_calendar import ReservationCalendar

def test_fvrc_legacy_compatibility():
    """
    Test against the example from the legacy Readme.
    2023-06-09 (Friday) should be Week 2, Weekday 5 (Friday).
    Next year reservations:
    2024-06-07
    ...
    2034-06-09
    """
    calendar = ReservationCalendar()
    date = datetime(2023, 6, 9)
    
    # Check week info
    week_number, weekday_number = calendar.get_week_info(date)
    assert week_number == 2
    assert weekday_number == 5
    assert calendar.get_day_name(date) == "Friday"
    
    # Check future dates
    expected_dates = {
        2024: datetime(2024, 6, 7),
        2025: datetime(2025, 6, 6),
        2026: datetime(2026, 6, 5),
        2027: datetime(2027, 6, 11),
        2028: datetime(2028, 6, 9),
        2029: datetime(2029, 6, 8),
        2030: datetime(2030, 6, 7),
        2031: datetime(2031, 6, 6),
        2032: datetime(2032, 6, 11),
        2033: datetime(2033, 6, 10),
        2034: datetime(2034, 6, 9)
    }
    
    for year, expected_date in expected_dates.items():
        calculated_date = calendar.get_reservation_start_date(date, year)
        assert calculated_date == expected_date, f"Failed for year {year}"

def test_memorial_day_logic():
    calendar = ReservationCalendar()
    # 2023 Memorial Day is May 29 (Monday)
    # Week Zero starts 8 days before: May 21 (Sunday)
    
    # Check Week Zero Start
    week_zero_start = calendar.get_week_start_date(2023, 0)
    assert week_zero_start == datetime(2023, 5, 21)
    
    # Check Week 1 Start (May 28)
    week_one_start = calendar.get_week_start_date(2023, 1)
    assert week_one_start == datetime(2023, 5, 28)

def test_edge_cases():
    calendar = ReservationCalendar()
    # Test date exactly on Week Zero start
    date = datetime(2023, 5, 21)
    week_num = calendar.get_week_number(date)
    assert week_num == 0
    
    # Test date before Week Zero (should be negative)
    res_date = datetime(2023, 5, 20)
    # 1 day before
    assert calendar.get_week_number(res_date) == -1
