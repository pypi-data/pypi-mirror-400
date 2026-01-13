import calendar
import datetime
from abc import ABC, abstractmethod


# calendar on Python 3.11 has not implement calendar.Month yet
# https://github.com/python/cpython/blob/3.11/Lib/calendar.py#L40
class Month:
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12


class Holiday(ABC):
    def __init__(self, key: str, summary: str, description: str):
        """
        Initialize a Holiday instance.

        Args:
            key: Unique identifier for the holiday.
            summary: The summary (title) of the holiday.
            description: A detailed description of the holiday.
        """
        self.key = key
        self.summary = summary
        self.description = description

    @staticmethod
    def get_weekdays_in_month(
        weekday: int = calendar.SUNDAY,
        year: int = datetime.date.today().year,
        month: int = datetime.date.today().month,
    ) -> list[datetime.date]:
        """
        Get a list of dates for a specific weekday in a given month and year.

        Args:
            weekday: The weekday to find (e.g., calendar.SUNDAY).
            year: The year.
            month: The month (1-12).

        Returns:
            A list of datetime.date objects representing the specific weekdays in the month.
        """
        cal = calendar.Calendar(calendar.SUNDAY)
        monthcal = cal.monthdatescalendar(year, month)
        month_weekdays = [
            day
            for week in monthcal
            for day in week
            if day.month == month and day.weekday() == weekday
        ]

        return month_weekdays

    @abstractmethod
    def get_date(self, year: int) -> datetime.date:
        """
        Calculate the date of the holiday for a given year.

        Args:
            year: The year to calculate the holiday date for.

        Returns:
            The date of the holiday.
        """
        pass


class MothersDay(Holiday):
    def __init__(self) -> None:
        super().__init__(
            key="mothers_day",
            summary="Mother's Day",
            description="Mother's Day is a celebration honoring the mother of the family or individual, as well as motherhood, maternal bonds, and the influence of mothers in society. It is celebrated on different days in many parts of the world, most commonly in the months of March or May.",
        )

    def get_date(self, year: int) -> datetime.date:
        return self.get_weekdays_in_month(calendar.SUNDAY, year, Month.MAY)[1]


class FathersDay(Holiday):
    def __init__(self) -> None:
        super().__init__(
            key="fathers_day",
            summary="Father's Day",
            description="Father's Day is a holiday of honoring fatherhood and paternal bonds, as well as the influence of fathers in society. In Catholic countries of Europe, it has been celebrated on March 19 as Saint Joseph's Day since the Middle Ages. In the United States, Father's Day was founded by Sonora Smart Dodd, and celebrated on the third Sunday of June for the first time in 1910.",
        )

    def get_date(self, year: int) -> datetime.date:
        return self.get_weekdays_in_month(calendar.SUNDAY, year, Month.JUNE)[2]


class ThanksgivingDay(Holiday):
    def __init__(self) -> None:
        super().__init__(
            key="thanksgiving_day",
            summary="Thanksgiving Day",
            description="Thanksgiving is a national holiday celebrated on various dates in the United States, Canada, Grenada, Saint Lucia, and Liberia. It began as a day of giving thanks for the blessing of the harvest and of the preceding year.",
        )

    def get_date(self, year: int) -> datetime.date:
        return self.get_weekdays_in_month(calendar.THURSDAY, year, Month.NOVEMBER)[3]


HOLIDAYS: dict[str, Holiday] = {
    h.key: h for h in [MothersDay(), FathersDay(), ThanksgivingDay()]
}
