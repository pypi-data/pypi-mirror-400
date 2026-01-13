from dataclasses import dataclass
from typing import Any, Type, TypeVar

from .prop import Prop
from .property import Property

T = TypeVar("T", bound="Status")


@dataclass
class Status(Property):
    status_id: str | None
    status_name: str
    status_color: str | None
    TYPE: str = "status"

    def __init__(
        self,
        name: str,
        status_name: str,
        id: str | None = None,
        status_id: str | None = None,
        status_color: str | None = None,
    ):
        self.name = name
        self.status_name = status_name
        self.id = id
        self.status_id = status_id
        self.status_color = status_color

    @classmethod
    def of(cls: Type[T], name: str, param: dict) -> T:
        return cls(
            name=name,
            status_name=param["status"]["name"],
            id=param["id"],
            status_id=param["status"]["id"],
            status_color=param["status"]["color"],
        )

    @classmethod
    def from_status_name(cls: Type[T], status_name: str, name: str | None = None) -> T:
        return cls(
            name=name or cls.PROP_NAME,
            status_name=status_name,
        )

    def __dict__(self):
        result = {
            "type": self.TYPE,
            "status": {
                "name": self.status_name,
            },
        }
        if self.status_id is not None:
            result["status"]["id"] = self.status_id
        if self.status_color is not None:
            result["status"]["color"] = self.status_color
        return {self.name: result}

    @property
    def _prop_type(self) -> Prop:
        return Prop.STATUS

    @property
    def _value_for_filter(self) -> Any:
        return self.status_name
