from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Type, TypeVar

from ..datetime_utils import convert_to_date_or_datetime
from .prop import Prop
from .property import Property

T = TypeVar("T", bound="Date")


@dataclass
class Date(Property):
    start: str | None = None
    end: str | None = None
    time_zone: str | None = None
    TYPE: str = "date"

    def __init__(
        self,
        name: str,
        id: str | None = None,  # noqa: A002
        start: str | None = None,
        end: str | None = None,
        time_zone: str | None = None,
    ) -> None:
        self.name = name
        self.id = id
        self.start = start
        self.end = end
        self.time_zone = time_zone

    @property
    def start_time(self) -> date | datetime | None:
        if self.start is None:
            return None
        return convert_to_date_or_datetime(self.start)

    @property
    def start_date(self) -> date | None:
        if self.start is None:
            return None
        return convert_to_date_or_datetime(self.start, cls=date)

    @property
    def start_datetime(self) -> datetime | None:
        if self.start is None:
            return None
        return convert_to_date_or_datetime(self.start, cls=datetime)

    @property
    def end_time(self) -> date | datetime | None:
        if self.end is None:
            return None
        return convert_to_date_or_datetime(self.end)

    @property
    def end_date(self) -> date | None:
        if self.end is None:
            return None
        return convert_to_date_or_datetime(self.end, cls=date)

    @property
    def end_datetime(self) -> datetime | None:
        if self.end is None:
            return None
        return convert_to_date_or_datetime(self.end, cls=datetime)

    @classmethod
    def of(cls: Type[T], name: str, param: dict | None = None) -> T:
        if param is None:
            param = {}
        if param["date"] is None:
            return cls(name=name, id=param["id"])
        return cls(
            name=name,
            id=param["id"],
            start=param["date"]["start"],
            end=param["date"]["end"],
            time_zone=param["date"]["time_zone"],
        )

    @classmethod
    def from_start_date(cls: Type[T], start_date: date | datetime | None = None, name: str | None = None) -> T:
        return cls(
            name=name or cls.PROP_NAME,
            start=start_date.isoformat() if start_date is not None else None,
        )

    @classmethod
    def from_range(
        cls: Type[T],
        start: date | datetime | None = None,
        end: date | datetime | None = None,
        name: str | None = None,
    ) -> T:
        if start is None:
            if end is not None:
                raise ValueError("Start date is required when end date is specified.")
            return cls(name=name or cls.PROP_NAME)
        return cls(
            name=name or cls.PROP_NAME,
            start=start.isoformat(),
            end=end.isoformat() if end is not None else None,
        )

    def is_between(self, start: datetime, end: datetime) -> bool:
        start_datetime = self.start_datetime
        if start_datetime is None:
            return True
        if start.timestamp() > start_datetime.timestamp():
            return False
        if start_datetime.timestamp() > end.timestamp():  # noqa: SIM103
            return False
        return True

    @property
    def date(self) -> date | None:
        return convert_to_date_or_datetime(self.start, cls=date)

    def __dict__(self) -> dict:
        # 未指定の場合を考慮している
        _date = (
            {
                "start": self.start,
                "end": self.end,
                "time_zone": self.time_zone,
            }
            if self.start is not None
            else None
        )
        return {
            self.name: {
                "type": self.TYPE,
                "date": _date,
            },
        }

    @property
    def _prop_type(self) -> Prop:
        return Prop.DATE

    @property
    def _value_for_filter(self) -> Any:
        if self.start is None:
            raise ValueError(f"{self.name}: date is required.")
        return self.start
