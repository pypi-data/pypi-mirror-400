from datetime import date, datetime, timedelta, timezone
from enum import Enum
from typing import TypeVar

JST = timezone(timedelta(hours=+9), "JST")

LENGTH_DATE = 10  # "YYYY-MM-DD"

D = TypeVar("D", bound=date)


class DateType(Enum):
    DATE = "date"
    DATETIME = "datetime"
    NONE = "none"

    @staticmethod
    def get_datetype(value: str) -> "DateType":
        try:
            # それぞれ変換できることを確認してから返却する
            if len(value) == LENGTH_DATE:
                date.fromisoformat(value)
                return DateType.DATE
            datetime.fromisoformat(value)
            return DateType.DATETIME
        except ValueError:
            return DateType.NONE


def jst_now() -> datetime:
    return datetime.now(JST)


def jst_today_datetime() -> datetime:
    return jst_now().replace(hour=0, minute=0, second=0, microsecond=0)


def jst_today(is_previous_day_until_2am: bool | None = None) -> date:
    """Return today's date in JST
    Args:
        isPreviousDayUntil2AM (bool): If True, return the previous day until 2AM. Defaults to None.
    Returns:
        date: today's date in JST
    """
    now = jst_now()
    if is_previous_day_until_2am:
        return now.date() - timedelta(days=1) if now.hour < 2 else now.date()
    return now.date()


def jst_tommorow() -> datetime:
    return jst_today_datetime() + timedelta(days=1)


def convert_to_date_or_datetime(value: str | None, cls: type[D] | None = None) -> D | None:
    if value is None:
        return None
    date_type = DateType.get_datetype(value)
    match date_type:
        case DateType.DATE:
            return _convert_date(value, cls)  # type: ignore
        case DateType.DATETIME:
            return _convert_datetime(value, cls)  # type: ignore
        case DateType.NONE:
            return None


def _convert_date(value: str, cls: type[D] | None) -> date | datetime:
    _date = date.fromisoformat(value)
    if cls is None:
        return _date
    if cls.__name__ != "datetime":
        return _date
    return datetime(_date.year, _date.month, _date.day, tzinfo=JST)


def _convert_datetime(value: str, cls: type[D] | None) -> date | datetime:
    _datetime = datetime.fromisoformat(value)
    if cls is None:
        if not __is_datatime(_datetime):
            return _datetime.date()
        return _datetime
    if cls.__name__ == "date":
        return _datetime.date()
    return _datetime


def __is_datatime(value: datetime) -> bool:
    return value.hour != 0 or value.minute != 0 or value.second != 0
