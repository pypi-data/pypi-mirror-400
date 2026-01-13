# noqa: A005

"""Date/Time SQL functions (https://mariadb.com/kb/en/date-time-functions/)."""

from enum import StrEnum
from typing import Any, Literal

from sqlfactory.func.base import Function
from sqlfactory.statement import Raw, Statement


class Interval(Statement):
    # pylint: disable=too-many-instance-attributes
    """
    INTERVAL statement for DATE_ADD, DATE_SUB and similar functions.
    """

    _ATTRIBUTES = (
        "microsecond",
        "second",
        "minute",
        "hour",
        "day",
        "week",
        "month",
        "quarter",
        "year",
        "second_microsecond",
        "minute_microsecond",
        "minute_second",
        "hour_microsecond",
        "hour_second",
        "hour_minute",
        "day_microsecond",
        "day_second",
        "day_minute",
        "day_hour",
        "year_month",
    )

    # pylint: disable=too-many-arguments, too-many-positional-arguments, too-many-locals
    def __init__(
        self,
        microsecond: Any = None,
        second: Any = None,
        minute: Any = None,
        hour: Any = None,
        day: Any = None,
        week: Any = None,
        month: Any = None,
        quarter: Any = None,
        year: Any = None,
        second_microsecond: Any = None,
        minute_microsecond: Any = None,
        minute_second: Any = None,
        hour_microsecond: Any = None,
        hour_second: Any = None,
        hour_minute: Any = None,
        day_microsecond: Any = None,
        day_second: Any = None,
        day_minute: Any = None,
        day_hour: Any = None,
        year_month: Any = None,
    ) -> None:
        super().__init__()

        self.microsecond = microsecond
        self.second = second
        self.minute = minute
        self.hour = hour
        self.day = day
        self.week = week
        self.month = month
        self.quarter = quarter
        self.year = year
        self.second_microsecond = second_microsecond
        self.minute_microsecond = minute_microsecond
        self.minute_second = minute_second
        self.hour_microsecond = hour_microsecond
        self.hour_second = hour_second
        self.hour_minute = hour_minute
        self.day_microsecond = day_microsecond
        self.day_second = day_second
        self.day_minute = day_minute
        self.day_hour = day_hour
        self.year_month = year_month

        if all(getattr(self, attr) is None for attr in self._ATTRIBUTES):
            raise ValueError("At least one attribute must be set.")

    def __str__(self) -> str:
        return "INTERVAL " + " ".join(
            f"{self.dialect.placeholder if not isinstance(getattr(self, attr), Statement) else str(getattr(self, attr))} "
            f"{attr.upper()}"
            for attr in reversed(self._ATTRIBUTES)
            if getattr(self, attr) is not None
        )

    @property
    def args(self) -> list[Any]:
        args = []

        for attr in reversed(self._ATTRIBUTES):
            value = getattr(self, attr)
            if value is None:
                continue

            if isinstance(value, Statement):
                args.extend(value.args)

            elif not isinstance(value, Statement):
                args.append(value)

        return args


class AddMonths(Function):
    """
    Adds months to date.
    """

    def __init__(self, date: Any, months: int) -> None:
        super().__init__("ADDMONTHS", date, months)


class AddDate(Function):
    """
    Adds days to date.
    """

    def __init__(self, date: Any, days: int | Interval) -> None:
        super().__init__("ADDDATE", date, days)


class AddTime(Function):
    """
    Adds time to date.
    """

    def __init__(self, date: Any, time: Any) -> None:
        super().__init__("ADDTIME", date, time)


class ConvertTz(Function):
    """
    Converts date from one timezone to another.
    """

    def __init__(self, date: Any, from_tz: str, to_tz: str) -> None:
        super().__init__("CONVERT_TZ", date, from_tz, to_tz)


class CurDate(Function):
    """
    Returns current date.
    """

    def __init__(self) -> None:
        super().__init__("CURDATE")


class CurrentDate(Function):
    """
    Returns current date.
    """

    def __init__(self) -> None:
        super().__init__("CURRENT_DATE")


class CurrentTime(Function):
    """
    Returns current time.
    """

    def __init__(self) -> None:
        super().__init__("CURRENT_TIME")


class CurrentTimestamp(Function):
    """
    Returns current timestamp.
    """

    def __init__(self) -> None:
        super().__init__("CURRENT_TIMESTAMP")


class CurTime(Function):
    """
    Returns current time.
    """

    def __init__(self) -> None:
        super().__init__("CURTIME")


class Date(Function):
    """
    Extracts date from datetime.
    """

    def __init__(self, date: Any) -> None:
        super().__init__("DATE", date)


class DateDiff(Function):
    """
    Returns difference between two dates.
    """

    def __init__(self, date1: Any, date2: Any) -> None:
        super().__init__("DATEDIFF", date1, date2)


class DateAdd(Function):
    """
    Adds interval to date.
    """

    def __init__(self, date: Any, interval: Interval) -> None:
        super().__init__("DATE_ADD", date, interval)


class DateFormat(Function):
    """
    Formats date.
    """

    def __init__(self, date: Any, date_format: str) -> None:
        super().__init__("DATE_FORMAT", date, date_format)


class DateSub(Function):
    """
    Subtracts interval from date.
    """

    def __init__(self, date: Any, interval: Interval) -> None:
        super().__init__("DATE_SUB", date, interval)


class Day(Function):
    """
    Extracts day from date.
    """

    def __init__(self, date: Any) -> None:
        super().__init__("DAY", date)


class DayName(Function):
    """
    Returns name of the day.
    """

    def __init__(self, date: Any) -> None:
        super().__init__("DAYNAME", date)


class DayOfMonth(Function):
    """
    Extracts day of month from date.
    """

    def __init__(self, date: Any) -> None:
        super().__init__("DAYOFMONTH", date)


class DayOfWeek(Function):
    """
    Extracts day of week from date.
    """

    def __init__(self, date: Any) -> None:
        super().__init__("DAYOFWEEK", date)


class DayOfYear(Function):
    """
    Extracts day of year from date.
    """

    def __init__(self, date: Any) -> None:
        super().__init__("DAYOFYEAR", date)


class Extract(Statement):
    """
    Extracts part of date.
    """

    def __init__(self, unit: str, date: Any) -> None:
        super().__init__()

        self._unit = unit
        self._date = date

    def __str__(self) -> str:
        return f"EXTRACT({self._unit} FROM {str(self._date) if isinstance(self._date, Statement) else self.dialect.placeholder})"

    @property
    def args(self) -> list[Any]:
        """Arguments for the Extract function."""
        return [self._date] if not isinstance(self._date, Statement) else self._date.args


class FormatPicoTime(Function):
    """
    Formats pico time.
    """

    def __init__(self, time: Any) -> None:
        super().__init__("FORMAT_PICO_TIME", time)


class FromDays(Function):
    """
    Converts days to date.
    """

    def __init__(self, days: Any) -> None:
        super().__init__("FROM_DAYS", days)


class FromUnixTime(Function):
    """
    Converts UNIX timestamp to date.
    """

    def __init__(self, unix_timestamp: Any) -> None:
        super().__init__("FROM_UNIXTIME", unix_timestamp)


class GetFormat(Function):
    """
    Returns date format.
    """

    def __init__(
        self, date_format: Literal["DATE", "DATETIME", "TIME"], locale: Literal["EUR", "USA", "JIS", "ISO", "INTERNAL"]
    ) -> None:
        super().__init__("GET_FORMAT", Raw(date_format), locale)


class Hour(Function):
    """
    Extracts hour from datetime.
    """

    def __init__(self, time: Any) -> None:
        super().__init__("HOUR", time)


class LastDay(Function):
    """
    Returns last day of month.
    """

    def __init__(self, date: Any) -> None:
        super().__init__("LAST_DAY", date)


class LocalTime(Function):
    """
    Returns local time.
    """

    def __init__(self) -> None:
        super().__init__("LOCALTIME")


class LocalTimestamp(Function):
    """
    Returns local timestamp.
    """

    def __init__(self) -> None:
        super().__init__("LOCALTIMESTAMP")


class MakeDate(Function):
    """
    Creates date from year and day of year.
    """

    def __init__(self, year: Any, day_of_year: Any) -> None:
        super().__init__("MAKEDATE", year, day_of_year)


class MakeTime(Function):
    """
    Creates time from hours, minutes, seconds.
    """

    def __init__(self, hours: Any, minutes: Any, seconds: Any) -> None:
        super().__init__("MAKETIME", hours, minutes, seconds)


class Microsecond(Function):
    """
    Extracts microseconds from datetime.
    """

    def __init__(self, time: Any) -> None:
        super().__init__("MICROSECOND", time)


class Minute(Function):
    """
    Extracts minutes from datetime.
    """

    def __init__(self, time: Any) -> None:
        super().__init__("MINUTE", time)


class Month(Function):
    """
    Returns a month from 1 to 12.
    """

    def __init__(self, time: Any) -> None:
        super().__init__("MONTH", time)


class MonthName(Function):
    """
    Returns name of the month.
    """

    def __init__(self, date: Any) -> None:
        super().__init__("MONTHNAME", date)


class Now(Function):
    """
    Returns current date and time.
    """

    def __init__(self) -> None:
        super().__init__("NOW")


class PeriodAdd(Function):
    """
    Add months to a period.
    """

    def __init__(self, date: Any, period: Any) -> None:
        super().__init__("PERIOD_ADD", date, period)


class PeriodDiff(Function):
    """
    Returns number of months between two periods.
    """

    def __init__(self, period1: Any, period2: Any) -> None:
        super().__init__("PERIOD_DIFF", period1, period2)


class Quarter(Function):
    """
    Extracts quarter from date.
    """

    def __init__(self, date: Any) -> None:
        super().__init__("QUARTER", date)


class Second(Function):
    """
    Extracts seconds from datetime.
    """

    def __init__(self, time: Any) -> None:
        super().__init__("SECOND", time)


class SecToTime(Function):
    """
    Converts seconds to time.
    """

    def __init__(self, seconds: Any) -> None:
        super().__init__("SEC_TO_TIME", seconds)


class StrToDate(Function):
    """
    Converts string to date.
    """

    def __init__(self, date: Any, date_format: str) -> None:
        super().__init__("STR_TO_DATE", date, date_format)


class SubDate(Function):
    """
    Subtracts days from date.
    """

    def __init__(self, date: Any, days: int | Interval) -> None:
        super().__init__("SUBDATE", date, days)


class SubTime(Function):
    """
    Subtracts time from date.
    """

    def __init__(self, date: Any, time: Any) -> None:
        super().__init__("SUBTIME", date, time)


class SysDate(Function):
    """
    Returns current date.
    """

    def __init__(self) -> None:
        super().__init__("SYSDATE")


class Time(Function):
    """
    Extracts time from datetime.
    """

    def __init__(self, time: Any) -> None:
        super().__init__("TIME", time)


class TimeDiff(Function):
    """
    Returns difference between two times.
    """

    def __init__(self, time1: Any, time2: Any) -> None:
        super().__init__("TIMEDIFF", time1, time2)


class Timestamp(Function):
    """
    Converts date to timestamp.
    """

    def __init__(self, date: Any) -> None:
        super().__init__("TIMESTAMP", date)


class TSUnit(StrEnum):
    """Valid units for `TimestampAdd` / `TimestampSub` functions."""

    MICROSECOND = "MICROSECOND"
    SECOND = "SECOND"
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    QUARTER = "QUARTER"
    YEAR = "YEAR"

    SQL_TSI_MICROSECOND = "SQL_TSI_MICROSECOND"
    SQL_TSI_SECOND = "SQL_TSI_SECOND"
    SQL_TSI_MINUTE = "SQL_TSI_MINUTE"
    SQL_TSI_HOUR = "SQL_TSI_HOUR"
    SQL_TSI_DAY = "SQL_TSI_DAY"
    SQL_TSI_WEEK = "SQL_TSI_WEEK"
    SQL_TSI_MONTH = "SQL_TSI_MONTH"
    SQL_TSI_QUARTER = "SQL_TSI_QUARTER"
    SQL_TSI_YEAR = "SQL_TSI_YEAR"


class TimestampAdd(Function):
    """
    Add interval to date or datetime.
    """

    def __init__(self, unit: TSUnit, interval: Any, date: Any) -> None:
        super().__init__("TIMESTAMPADD", Raw(unit.value), interval, date)


class TimestampDiff(Function):
    """
    Difference between two datetimes.
    """

    def __init__(self, unit: TSUnit, datetime_expr1: Any, datetime_expr2: Any) -> None:
        super().__init__("TIMESTAMPDIFF", Raw(unit.value), datetime_expr1, datetime_expr2)


class TimeFormat(Function):
    """
    Formats time.
    """

    def __init__(self, time: Any, date_format: str) -> None:
        super().__init__("TIME_FORMAT", time, date_format)


class TimeToSec(Function):
    """
    Converts time to seconds.
    """

    def __init__(self, time: Any) -> None:
        super().__init__("TIME_TO_SEC", time)


class ToDays(Function):
    """
    Converts date to days.
    """

    def __init__(self, date: Any) -> None:
        super().__init__("TO_DAYS", date)


class ToSeconds(Function):
    """
    Converts date to seconds.
    """

    def __init__(self, date: Any) -> None:
        super().__init__("TO_SECONDS", date)


class UnixTimestamp(Function):
    """
    Returns UNIX timestamp.
    """

    def __init__(self) -> None:
        super().__init__("UNIX_TIMESTAMP")


class UtcDate(Function):
    """
    Returns current date in UTC.
    """

    def __init__(self) -> None:
        super().__init__("UTC_DATE")


class UtcTime(Function):
    """
    Returns current time in UTC.
    """

    def __init__(self) -> None:
        super().__init__("UTC_TIME")


class UtcTimestamp(Function):
    """
    Returns current timestamp in UTC.
    """

    def __init__(self) -> None:
        super().__init__("UTC_TIMESTAMP")


class Week(Function):
    """
    Returns week number.
    """

    def __init__(self, date: Any, mode: int | Statement | None = None) -> None:
        if mode is not None:
            super().__init__("WEEK", date, mode)
        else:
            super().__init__("WEEK", date)


class WeekDay(Function):
    """
    Returns day of week.
    """

    def __init__(self, date: Any) -> None:
        super().__init__("WEEKDAY", date)


class WeekOfYear(Function):
    """
    Returns week of year.
    """

    def __init__(self, date: Any) -> None:
        super().__init__("WEEKOFYEAR", date)


class Year(Function):
    """
    Extracts year from date.
    """

    def __init__(self, date: Any) -> None:
        super().__init__("YEAR", date)


class YearWeek(Function):
    """
    Returns year and week number.
    """

    def __init__(self, date: Any, mode: int | Statement | None = None) -> None:
        if mode is None:
            super().__init__("YEARWEEK", date)
        else:
            super().__init__("YEARWEEK", date, mode)
