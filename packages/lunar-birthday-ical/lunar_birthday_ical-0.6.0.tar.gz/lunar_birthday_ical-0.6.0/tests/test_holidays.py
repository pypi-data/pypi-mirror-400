import calendar
import datetime

from lunar_birthday_ical.holidays import (
    FathersDay,
    Holiday,
    MothersDay,
    ThanksgivingDay,
)


def test_get_weekdays_in_month():
    # Test case: Get all Sundays in May 2023
    year = 2023
    month = 5
    weekday = calendar.SUNDAY
    expected_dates = [
        datetime.date(2023, 5, 7),
        datetime.date(2023, 5, 14),
        datetime.date(2023, 5, 21),
        datetime.date(2023, 5, 28),
    ]
    assert Holiday.get_weekdays_in_month(weekday, year, month) == expected_dates


def test_get_mothers_day():
    # Test case: Mother's Day in 2023
    year = 2023
    expected_date = datetime.date(2023, 5, 14)
    assert MothersDay().get_date(year) == expected_date


def test_get_fathers_day():
    # Test case: Father's Day in 2023
    year = 2023
    expected_date = datetime.date(2023, 6, 18)
    assert FathersDay().get_date(year) == expected_date


def test_get_thanksgiving_day():
    # Test case: Thanksgiving Day in 2023 (US)
    year = 2023
    expected_date = datetime.date(2023, 11, 23)
    assert ThanksgivingDay().get_date(year) == expected_date
