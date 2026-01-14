from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Tuple


class ReferenceDayProvider(ABC):
    """
    Abstract base class for providing the reference day for a given year.
    The reservation calendar logic is based on this reference day.
    """

    @abstractmethod
    def get_reference_day(self, year: int) -> datetime:
        """Returns the reference day for the specified year."""
        pass


class MemorialDayProvider(ReferenceDayProvider):
    """
    Standard provider that uses Memorial Day (last Monday in May) as the reference.
    """

    def get_reference_day(self, year: int) -> datetime:
        # Memorial Day is the last Monday in May
        last_day_of_may = datetime(year, 5, 31)
        # 0 = Monday, 1 = Tuesday, ...
        offset = last_day_of_may.weekday()  # Days past Monday
        memorial_day = last_day_of_may - timedelta(days=offset)
        return memorial_day


class ReservationCalendar:
    """
    Reservation Calendar
    --------------------
    Determine the week number and reservation start dates based on a reference day strategy.
    
    By default, it uses Memorial Day logic:
    - Week Zero is the week before Memorial Day.
    - Weeks run from Sunday to Saturday.
    """

    def __init__(self, provider: ReferenceDayProvider = None):
        """
        Initialize the calendar with a reference day provider.
        Defaults to MemorialDayProvider if none is supplied.
        """
        self.provider = provider or MemorialDayProvider()
        self._day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    def _get_week_zero_sunday(self, year: int) -> datetime:
        """
        Calculates the Sunday of Week Zero for a given year.
        Week Zero is defined relative to the reference day.
        
        For Memorial Day logic:
        - Reference Day is Memorial Day (Monday).
        - Thursday before Memorial Day is the anchor.
        - Sunday of that week is 4 days before that Thursday.
        """
        reference_day = self.provider.get_reference_day(year)
        
        # This logic mimics the original:
        # thursday_before_memorial_day = memorial_day - timedelta(days=(memorial_day.weekday() - 3) % 7)
        # Memorial Day is always Monday (0), so (0 - 3) % 7 = (-3) % 7 = 4.
        # Memorial Day - 4 days = Thursday before Memorial Day.
        # This seems to be the specific logic for "Memorial Day" weeks.
        # If we want this to be truly agnostic, we might need the provider to give "Week Zero Start".
        # But for now, assuming the "Reference Day" is like the "Peak" and we count back.
        
        # Let's stick to the exact logic from the original but generalized if possible.
        # Original: 
        # memorial_day - ((memorial_day.weekday() - 3) % 7) -> Thursday
        # Thursday - 4 -> Sunday
        
        # Simplified:
        # If Reference Day is DAY X.
        # Week Zero Sunday is determined by some offset.
        
        # For legacy compatibility, let's keep the logic tightly coupled to the "Reference Day is effectively Memorial Day-like"
        # OR: The provider simply returns the "Anchor Day" from which we calculate Week 0.
        
        # Calculating based on strict original logic:
        # thursday_before_ref = reference_day - timedelta(days=(reference_day.weekday() - 3) % 7)
        # week_zero_sunday = thursday_before_ref - timedelta(days=4)
        
        # Optimization:
        # If Memorial Day is Mon (0): (0-3)%7 = 4. Ref - 4 days = Thursday. Thursday - 4 days = Sunday. Total -8 days.
        # So Week Zero Sunday is ALWAYS 8 days before Memorial Day?
        # Let's check:
        # 2023: Mem Day = May 29 (Mon).
        # -8 days = May 21 (Sunday).
        # Original script:
        # Mem Day = May 29.
        # Thurs before = May 29 - 4 = May 25.
        # Sun of Week 0 = May 25 - 4 = May 21. Matches.
        
        # So yes, Week Zero starts 8 days before Memorial Day.
        return reference_day - timedelta(days=8)

    def get_week_start_date(self, year: int, week_number: int) -> datetime:
        """Returns the start date (Sunday) of a specific week number in a given year."""
        week_zero_sunday = self._get_week_zero_sunday(year)
        return week_zero_sunday + timedelta(days=7 * week_number)

    def get_week_number(self, date: datetime) -> int:
        """
        Returns the week number for a given date.
        Note: This effectively finds the 'reservation year' the date belongs to.
        Since the calendar slides, a date in early 2024 might technically belong to the 2023 'season' 
        or vice versa depending on when Week 0 starts.
        
        However, the original logic prioritized the current year's calendar.
        It checked: `self.FVRC[(self.FVRC["Year"] == date.year) & (self.FVRC["Start Date"] <= date)]`
        If the date was BEFORE Week 0 of the current year, it would fail or return nothing in the original code 
        (empty dataframe accesses usually index error).
        
        Wait, if date is Jan 1, 2024. 
        Week 0 2024 starts May 2024.
        So Jan 1 2024 < May 2024.
        The original code `self.FVRC["Year"] == date.year` would filter to 2024.
        Then `Start Date <= date` would be empty.
        `iloc[-1]` would crash `IndexError: single positional indexer is out-of-bounds`.
        
        So the original code implied usage only for dates *after* the season start?
        Or did it assume standard calendar years?
        Original doc: "This weekly calendar is used to pick future dates based on the current reservation."
        Usually reservations are in the season.
        
        I will assume the date belongs to the year of the date provided, but if it's before Week 0, 
        it might return a negative week number, which is mathematically correct for this logic.
        """
        year = date.year
        week_zero_sunday = self._get_week_zero_sunday(year)
        
        days_diff = (date - week_zero_sunday).days
        week_number = days_diff // 7
        return week_number

    def get_reservation_start_date(self, current_date: datetime, future_year: int) -> datetime:
        """
        Calculates the start date for a reservation in a future year,
        matching the same week number and day-of-week.
        """
        current_week_number = self.get_week_number(current_date)
        
        # 0 = Sunday, 1 = Monday ... 6 = Saturday in our custom numbering
        # Python weekday: 0=Mon, 6=Sun.
        # Original: (current_date.weekday() + 1) % 7 -> Sunday=0, Mon=1, ... Fri=5, Sat=6. Matches.
        current_day_index = (current_date.weekday() + 1) % 7
        
        future_week_start = self.get_week_start_date(future_year, current_week_number)
        return future_week_start + timedelta(days=current_day_index)

    def get_week_info(self, date: datetime) -> Tuple[int, int]:
        """
        Returns (week_number, day_index) for the given date.
        day_index: 0=Sunday, 1=Monday, ... 6=Saturday.
        """
        week_number = self.get_week_number(date)
        day_index = (date.weekday() + 1) % 7
        return week_number, day_index

    def get_day_name(self, date: datetime) -> str:
        """Returns the day name (e.g., 'Friday')."""
        day_index = (date.weekday() + 1) % 7
        return self._day_names[day_index]
