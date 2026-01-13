from dataclasses import dataclass
from typing import Any, Type, TypeVar

from .property import Property

T = TypeVar("T", bound="LastEditedBy")


@dataclass
class LastEditedBy(Property):
    TYPE: str = "last_edited_by"

    def __init__(
        self,
        name: str,
        last_edited_by: dict,
        id: str | None = None,  # noqa: A002
    ) -> None:
        self.name = name
        self.last_edited_by = last_edited_by
        self.id = id

    @classmethod
    def of(cls: Type[T], key: str, param: dict) -> T:
        return cls(id=param["id"], name=key, last_edited_by=param["last_edited_by"])

    def __dict__(self) -> dict[str, Any]:
        return {
            self.name: {
                "id": self.id,
                "type": self.TYPE,
                "last_edited_by": self.last_edited_by,
            },
        }

    @property
    def _prop_type(self):
        raise ValueError(f"{self.__class__.__name__} doesn't need a property type")

    @property
    def _value_for_filter(self):
        raise ValueError(f"{self.__class__.__name__} doesn't need a value for filter")
