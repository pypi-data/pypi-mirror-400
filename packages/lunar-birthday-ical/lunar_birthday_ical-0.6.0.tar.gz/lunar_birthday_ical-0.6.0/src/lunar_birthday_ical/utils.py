import datetime
import logging
import zoneinfo

from lunar_python import Lunar, LunarYear

logger = logging.getLogger(__name__)


def get_local_datetime(
    local_date: datetime.date | str,
    local_time: datetime.time | str,
    timezone: zoneinfo.ZoneInfo,
) -> datetime.datetime:
    if not isinstance(local_date, datetime.date):
        local_date = datetime.datetime.strptime(local_date, "%Y-%m-%d").date()
    if not isinstance(local_time, datetime.time):
        local_time = datetime.datetime.strptime(local_time, "%H:%M:%S").time()

    local_datetime = datetime.datetime.combine(local_date, local_time, timezone)

    return local_datetime


def local_datetime_to_utc_datetime(
    local_datetime: datetime.datetime,
) -> datetime.datetime:
    # 将 local_datetime "强制"转换为 UTC 时间, 注意 local_datetime 需要携带 tzinfo 信息
    utc = zoneinfo.ZoneInfo("UTC")
    # 这里宁可让它抛出错误信息, 也不要设置 默认值
    utc_datetime = local_datetime.replace(tzinfo=utc) - local_datetime.utcoffset()

    return utc_datetime


def get_future_solar_datetime(
    solar_datetime: datetime.datetime, target_year: int
) -> datetime.datetime:
    """
    Calculate the solar datetime for the same lunar date in a target year.

    The conversion logic is as follows:
    1. Convert the input `solar_datetime` to its corresponding lunar date.
    2. Extract the lunar month and day from this lunar date.
    3. Determine the corresponding lunar date in the `target_year`:
       - If the original date falls in a leap month, check if the `target_year` has the same leap month.
         If so, use the leap month; otherwise, use the corresponding non-leap month.
       - If the original date falls in a non-leap month, use the same month in the `target_year`.
       - Adjust the day if the target month has fewer days than the original day (e.g., 30th day in a 29-day month).
    4. Convert the resulting lunar date in the `target_year` back to a solar date.
    5. Combine the new solar date with the time and timezone from the original `solar_datetime`.

    Args:
        solar_datetime: The original solar datetime.
        target_year: The target year to find the corresponding lunar date in.

    Returns:
        The solar datetime corresponding to the same lunar date in the target year.
    """
    # 计算给定 公历日期 对应的 农历日期
    # Lunar.fromDate 所接受的类型为 datetime.datetime, 实际上处理后会把 time 部分丢弃
    lunar_date = Lunar.fromDate(solar_datetime)
    target_lunar_year = LunarYear.fromYear(target_year)

    # 获取目标农历年的闰月
    # 获取闰月 :return: 闰月数字, 1代表闰1月, 0代表无闰月
    leap_month = target_lunar_year.getLeapMonth()

    # 确定目标年份的农历月, 闰月使用负数, 非闰月使用正数
    if lunar_date.getMonth() > 0:
        target_lunar_month = target_lunar_year.getMonth(lunar_date.getMonth())
    elif abs(lunar_date.getMonth()) == leap_month:
        target_lunar_month = target_lunar_year.getMonth(lunar_date.getMonth())
    else:
        target_lunar_month = target_lunar_year.getMonth(abs(lunar_date.getMonth()))

    # 确定农历日
    target_lunar_day = min(lunar_date.getDay(), target_lunar_month.getDayCount())

    # 创建目标年份的农历日期
    target_lunar_date = Lunar.fromYmd(
        target_year, target_lunar_month.getMonth(), target_lunar_day
    )

    # 转换为公历日期, 恢复原本的时间和 timezone
    solar_time = solar_datetime.time()
    target_solar_datetime = datetime.datetime.strptime(
        target_lunar_date.getSolar().toYmd(), "%Y-%m-%d"
    ).replace(
        hour=solar_time.hour,
        minute=solar_time.minute,
        second=solar_time.second,
        tzinfo=solar_datetime.tzinfo,
    )

    return target_solar_datetime
