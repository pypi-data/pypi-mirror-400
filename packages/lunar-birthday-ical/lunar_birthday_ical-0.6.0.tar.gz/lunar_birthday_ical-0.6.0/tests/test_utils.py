import datetime
import zoneinfo

from lunar_birthday_ical.utils import (
    get_future_solar_datetime,
    get_local_datetime,
    local_datetime_to_utc_datetime,
)


def test_get_local_datetime():
    local_date = "2023-10-01"
    local_time = "12:00:00"
    timezone = zoneinfo.ZoneInfo("UTC")
    result = get_local_datetime(local_date, local_time, timezone)
    expected = datetime.datetime(2023, 10, 1, 12, 0, tzinfo=timezone)
    assert result == expected


def test_local_datetime_to_utc_datetime():
    local_datetime = datetime.datetime(
        2023, 10, 1, 12, 0, tzinfo=zoneinfo.ZoneInfo("Asia/Shanghai")
    )
    result = local_datetime_to_utc_datetime(local_datetime)
    expected = datetime.datetime(2023, 10, 1, 4, 0, tzinfo=zoneinfo.ZoneInfo("UTC"))
    assert result == expected


def test_first_day_of_gregorian_year():
    """
    Test case 1: 公历 2020-01-01 对应的农历日 二〇一九年腊月初七 在农历 二〇二〇年腊月初七 的公历日
    """
    solar_date = datetime.datetime(2020, 1, 1)
    target_year = 2020
    expected_date = datetime.datetime(2021, 1, 19)
    assert get_future_solar_datetime(solar_date, target_year) == expected_date


def test_last_day_of_gregorian_year():
    """
    Test case 2: 公历 2020-12-31 对应的农历日 二〇二〇年冬月十七 在农历 二〇二一年冬月十七 对应的公历日
    """
    solar_date = datetime.datetime(2020, 12, 31)
    target_year = 2021
    expected_date = datetime.datetime(2021, 12, 20)
    assert get_future_solar_datetime(solar_date, target_year) == expected_date


def test_lunar_new_year_to_next_lunar_new_year():
    """
    Test case 3: 公历 2020-01-25 对应的农历日 农历二〇二〇年正月初一 在农历 二〇二一年正月初一 对应的公历日
    """
    solar_date = datetime.datetime(2020, 1, 25)
    target_year = 2021
    expected_date = datetime.datetime(2021, 2, 12)
    assert get_future_solar_datetime(solar_date, target_year) == expected_date


def test_last_day_of_lunar_year_to_next_last_day_of_lunar_year():
    """
    Test case 4: 公历 2021-02-11 对应的农历日 二〇二〇年腊月三十 在农历 二〇二一年腊月廿九 对应的公历日 (农历 二〇二一年腊月 没有三十)
    """
    solar_date = datetime.datetime(2021, 2, 11)
    target_year = 2021
    expected_date = datetime.datetime(2022, 1, 31)
    assert get_future_solar_datetime(solar_date, target_year) == expected_date


def test_leap_month_to_next_leap_month():
    """
    Test case 5: 公历 2020-05-23 对应的农历日 二〇二〇年闰四月初一 在农历 二〇二一年四月初一 对应的公历日 (农历二〇二一年 没有闰四月)
    """
    solar_date = datetime.datetime(2020, 5, 23)
    target_year = 2021
    expected_date = datetime.datetime(2021, 5, 12)
    assert get_future_solar_datetime(solar_date, target_year) == expected_date


def test_utc_timezone():
    """
    Test case 6: 公历 2020-01-25 对应的农历日 二〇二〇年腊月十三 在农历 二〇二一年腊月十三 对应的公历日 (UTC 时区)
    """
    solar_date = datetime.datetime(2020, 1, 25, 15, 30, tzinfo=datetime.timezone.utc)
    target_year = 2021
    expected_date = datetime.datetime(2021, 2, 12, 15, 30, tzinfo=datetime.timezone.utc)
    assert get_future_solar_datetime(solar_date, target_year) == expected_date


def test_different_timezone():
    """
    Test case 7: 公历 2020-01-25 对应的农历日 二〇二〇年腊月十三 在农历 二〇二一年腊月十三 对应的公历日 (UTC+8 时区)
    """
    solar_date = datetime.datetime(
        2020, 1, 25, 15, 30, tzinfo=datetime.timezone(datetime.timedelta(hours=8))
    )
    target_year = 2021
    expected_date = datetime.datetime(
        2021, 2, 12, 15, 30, tzinfo=datetime.timezone(datetime.timedelta(hours=8))
    )
    assert get_future_solar_datetime(solar_date, target_year) == expected_date


def test_large_age_increment():
    """
    Test case 8: 公历 2000-01-01 对应的农历日 一九九九年冬月廿五 在农历 二〇二〇年冬月廿五 对应的公历日
    """
    solar_date = datetime.datetime(2000, 1, 1)
    target_year = 2020
    expected_date = datetime.datetime(2021, 1, 8)
    assert get_future_solar_datetime(solar_date, target_year) == expected_date


def test_negative_age_increment():
    """
    Test case 9: 公历 2020-01-25 对应的农历日 二〇二〇年正月初一 在农历 二〇一九年正月初一 对应的公历日
    """
    solar_date = datetime.datetime(2020, 1, 25)
    target_year = 2019
    expected_date = datetime.datetime(2019, 2, 5)
    assert get_future_solar_datetime(solar_date, target_year) == expected_date
