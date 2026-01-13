from dataclasses import dataclass
from typing import Any, Type, TypeVar

from .prop import Prop
from .property import Property

T = TypeVar("T", bound="Url")


@dataclass
class Url(Property):
    url: str = ""

    TYPE: str = "rich_text"
    PROP_NAME = "url"  # 自分で使うために準備。本来は不要。

    def __init__(self, name: str, url: str = "", id: str | None = None):
        self.name = name
        self.url = url
        self.id = id

    @classmethod
    def of(cls: Type[T], name: str, param: dict) -> T:
        url = param["url"] if param.get("url") else ""
        return cls(
            name=name,
            url=url,
            id=param["id"],
        )

    @classmethod
    def from_url(cls: Type[T], url: str, name: str | None = None) -> T:
        return cls(
            name=name or cls.PROP_NAME,
            url=url,
        )

    @classmethod
    def empty(cls: Type[T], name: str | None = None) -> T:
        return cls(name=name or cls.PROP_NAME)

    def __dict__(self):
        result = {
            "type": "url",
            "url": self.url if self.url != "" else None,
        }
        if self.id is not None:
            result["id"] = self.id
        return {
            self.name: result,
        }

    @property
    def _prop_type(self) -> Prop:
        return Prop.RICH_TEXT

    @property
    def _value_for_filter(self) -> Any:
        return self.url
