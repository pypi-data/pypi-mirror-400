"""
Date and time functions for ClickHouse.
"""

from typing import Union
from chpy.orm import Column
from chpy.functions.base import Function


def now() -> Function:
    """Returns current date and time."""
    return Function("now")


def today() -> Function:
    """Returns current date."""
    return Function("today")


def yesterday() -> Function:
    """Returns yesterday's date."""
    return Function("yesterday")


def timeSlot(datetime: Union[Column, str]) -> Function:
    """Rounds to time slot."""
    return Function("timeSlot", datetime)


def toYear(x: Union[Column, str]) -> Function:
    """Extracts year."""
    return Function("toYear", x)


def toQuarter(x: Union[Column, str]) -> Function:
    """Extracts quarter."""
    return Function("toQuarter", x)


def toMonth(x: Union[Column, str]) -> Function:
    """Extracts month."""
    return Function("toMonth", x)


def toWeek(x: Union[Column, str]) -> Function:
    """Extracts week number."""
    return Function("toWeek", x)


def toDayOfYear(x: Union[Column, str]) -> Function:
    """Extracts day of year."""
    return Function("toDayOfYear", x)


def toDayOfMonth(x: Union[Column, str]) -> Function:
    """Extracts day of month."""
    return Function("toDayOfMonth", x)


def toDayOfWeek(x: Union[Column, str]) -> Function:
    """Extracts day of week."""
    return Function("toDayOfWeek", x)


def toHour(x: Union[Column, str]) -> Function:
    """Extracts hour."""
    return Function("toHour", x)


def toMinute(x: Union[Column, str]) -> Function:
    """Extracts minute."""
    return Function("toMinute", x)


def toSecond(x: Union[Column, str]) -> Function:
    """Extracts second."""
    return Function("toSecond", x)


def toStartOfYear(x: Union[Column, str]) -> Function:
    """Returns start of year."""
    return Function("toStartOfYear", x)


def toStartOfQuarter(x: Union[Column, str]) -> Function:
    """Returns start of quarter."""
    return Function("toStartOfQuarter", x)


def toStartOfMonth(x: Union[Column, str]) -> Function:
    """Returns start of month."""
    return Function("toStartOfMonth", x)


def toStartOfWeek(x: Union[Column, str]) -> Function:
    """Returns start of week."""
    return Function("toStartOfWeek", x)


def toStartOfDay(x: Union[Column, str]) -> Function:
    """Returns start of day."""
    return Function("toStartOfDay", x)


def toStartOfHour(x: Union[Column, str]) -> Function:
    """Returns start of hour."""
    return Function("toStartOfHour", x)


def toStartOfMinute(x: Union[Column, str]) -> Function:
    """Returns start of minute."""
    return Function("toStartOfMinute", x)


def toStartOfSecond(x: Union[Column, str]) -> Function:
    """Returns start of second."""
    return Function("toStartOfSecond", x)


def toStartOfFiveMinute(x: Union[Column, str]) -> Function:
    """Returns start of 5-minute interval."""
    return Function("toStartOfFiveMinute", x)


def toStartOfTenMinute(x: Union[Column, str]) -> Function:
    """Returns start of 10-minute interval."""
    return Function("toStartOfTenMinute", x)


def toStartOfFifteenMinute(x: Union[Column, str]) -> Function:
    """Returns start of 15-minute interval."""
    return Function("toStartOfFifteenMinute", x)


def toTime(x: Union[Column, str]) -> Function:
    """Converts to Time."""
    return Function("toTime", x)


def toRelativeYearNum(x: Union[Column, str]) -> Function:
    """Relative year number."""
    return Function("toRelativeYearNum", x)


def toRelativeQuarterNum(x: Union[Column, str]) -> Function:
    """Relative quarter number."""
    return Function("toRelativeQuarterNum", x)


def toRelativeMonthNum(x: Union[Column, str]) -> Function:
    """Relative month number."""
    return Function("toRelativeMonthNum", x)


def toRelativeWeekNum(x: Union[Column, str]) -> Function:
    """Relative week number."""
    return Function("toRelativeWeekNum", x)


def toRelativeDayNum(x: Union[Column, str]) -> Function:
    """Relative day number."""
    return Function("toRelativeDayNum", x)


def toRelativeHourNum(x: Union[Column, str]) -> Function:
    """Relative hour number."""
    return Function("toRelativeHourNum", x)


def toRelativeMinuteNum(x: Union[Column, str]) -> Function:
    """Relative minute number."""
    return Function("toRelativeMinuteNum", x)


def toRelativeSecondNum(x: Union[Column, str]) -> Function:
    """Relative second number."""
    return Function("toRelativeSecondNum", x)


def toISOYear(x: Union[Column, str]) -> Function:
    """ISO year."""
    return Function("toISOYear", x)


def toISOWeek(x: Union[Column, str]) -> Function:
    """ISO week number."""
    return Function("toISOWeek", x)


def toISOYearWeek(x: Union[Column, str]) -> Function:
    """ISO year and week."""
    return Function("toISOYearWeek", x)


def toMonday(x: Union[Column, str]) -> Function:
    """Returns Monday of week."""
    return Function("toMonday", x)


def toYYYYMM(x: Union[Column, str]) -> Function:
    """Returns YYYYMM format."""
    return Function("toYYYYMM", x)


def toYYYYMMDD(x: Union[Column, str]) -> Function:
    """Returns YYYYMMDD format."""
    return Function("toYYYYMMDD", x)


def toYYYYMMDDhhmmss(x: Union[Column, str]) -> Function:
    """Returns YYYYMMDDhhmmss format."""
    return Function("toYYYYMMDDhhmmss", x)


def addYears(x: Union[Column, str], n: int) -> Function:
    """Adds n years."""
    return Function("addYears", x, n)


def addQuarters(x: Union[Column, str], n: int) -> Function:
    """Adds n quarters."""
    return Function("addQuarters", x, n)


def addMonths(x: Union[Column, str], n: int) -> Function:
    """Adds n months."""
    return Function("addMonths", x, n)


def addWeeks(x: Union[Column, str], n: int) -> Function:
    """Adds n weeks."""
    return Function("addWeeks", x, n)


def addDays(x: Union[Column, str], n: int) -> Function:
    """Adds n days."""
    return Function("addDays", x, n)


def addHours(x: Union[Column, str], n: int) -> Function:
    """Adds n hours."""
    return Function("addHours", x, n)


def addMinutes(x: Union[Column, str], n: int) -> Function:
    """Adds n minutes."""
    return Function("addMinutes", x, n)


def addSeconds(x: Union[Column, str], n: int) -> Function:
    """Adds n seconds."""
    return Function("addSeconds", x, n)


def subtractYears(x: Union[Column, str], n: int) -> Function:
    """Subtracts n years."""
    return Function("subtractYears", x, n)


def subtractQuarters(x: Union[Column, str], n: int) -> Function:
    """Subtracts n quarters."""
    return Function("subtractQuarters", x, n)


def subtractMonths(x: Union[Column, str], n: int) -> Function:
    """Subtracts n months."""
    return Function("subtractMonths", x, n)


def subtractWeeks(x: Union[Column, str], n: int) -> Function:
    """Subtracts n weeks."""
    return Function("subtractWeeks", x, n)


def subtractDays(x: Union[Column, str], n: int) -> Function:
    """Subtracts n days."""
    return Function("subtractDays", x, n)


def subtractHours(x: Union[Column, str], n: int) -> Function:
    """Subtracts n hours."""
    return Function("subtractHours", x, n)


def subtractMinutes(x: Union[Column, str], n: int) -> Function:
    """Subtracts n minutes."""
    return Function("subtractMinutes", x, n)


def subtractSeconds(x: Union[Column, str], n: int) -> Function:
    """Subtracts n seconds."""
    return Function("subtractSeconds", x, n)


def dateDiff(unit: str, start: Union[Column, str], end: Union[Column, str]) -> Function:
    """Returns difference in specified unit."""
    return Function("dateDiff", unit, start, end)


def dateName(part: str, date: Union[Column, str]) -> Function:
    """Returns name of date part."""
    return Function("dateName", part, date)


def timeZone() -> Function:
    """Returns timezone."""
    return Function("timeZone")


def timeZoneOf(x: Union[Column, str]) -> Function:
    """Returns timezone of datetime."""
    return Function("timeZoneOf", x)


def toTimeZone(x: Union[Column, str], timezone: str) -> Function:
    """Converts to timezone."""
    return Function("toTimeZone", x, timezone)


def formatDateTime(x: Union[Column, str], format: str) -> Function:
    """Formats datetime."""
    return Function("formatDateTime", x, format)


def parseDateTimeBestEffort(x: Union[Column, str]) -> Function:
    """Parses datetime from string."""
    return Function("parseDateTimeBestEffort", x)

