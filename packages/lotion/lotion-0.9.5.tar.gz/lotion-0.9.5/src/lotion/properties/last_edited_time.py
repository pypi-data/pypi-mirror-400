from dataclasses import dataclass
from datetime import datetime
from typing import Any, Type, TypeVar

from ..datetime_utils import convert_to_date_or_datetime
from .property import Property

T = TypeVar("T", bound="LastEditedTime")


@dataclass
class LastEditedTime(Property):
    TYPE: str = "date"

    def __init__(
        self,
        name: str,
        value: datetime,
        id: str | None = None,  # noqa: A002
    ) -> None:
        self.name = name
        self.value = value
        self.id = id

    @classmethod
    def create(cls: Type[T], key, value: str) -> T:
        return cls(
            name=key,
            value=convert_to_date_or_datetime(value),
        )

    def __dict__(self) -> dict[str, Any]:
        _date = {
            "start": self.value.isoformat(),
            "end": None,
            "time_zone": None,
        }
        return {
            self.name: {
                "type": self.TYPE,
                "date": _date,
            },
        }

    @property
    def _prop_type(self):
        raise ValueError(f"{self.__class__.__name__} doesn't need a property type")

    @property
    def _value_for_filter(self):
        raise ValueError(f"{self.__class__.__name__} doesn't need a value for filter")
