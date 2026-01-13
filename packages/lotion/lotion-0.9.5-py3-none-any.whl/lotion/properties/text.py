from dataclasses import dataclass
from typing import Any, Type, TypeVar

from ..block.rich_text import RichText
from .prop import Prop
from .property import Property

T = TypeVar("T", bound="Text")


@dataclass
class Text(Property):
    rich_text: RichText
    TYPE: str = "rich_text"

    def __init__(
        self,
        name: str,
        rich_text: RichText,
        id: str | None = None,
    ) -> None:  # noqa: A002
        self.name = name
        self.id = id
        self.rich_text = rich_text

    @classmethod
    def from_dict(cls: Type[T], name: str, param: dict) -> T:
        rich_text = RichText.from_entity(param["rich_text"])
        id = param["id"]
        return cls(
            name=name,
            id=id,
            rich_text=rich_text,
        )

    def __dict__(self):
        result = {
            "type": self.TYPE,
            "rich_text": self.rich_text.to_dict(),
        }
        return {self.name: result}

    def append_text(self, text: str):
        updated_text = self.text + "\n" + text
        cls = self.__class__
        return cls(
            name=self.name,
            rich_text=RichText.from_plain_text(updated_text.strip()),
        )

    @classmethod
    def from_plain_text(cls: Type[T], text: str, name: str | None = None) -> T:
        return cls(
            name=name or cls.PROP_NAME,
            rich_text=RichText.from_plain_text(text=text),
        )

    @classmethod
    def from_rich_text(cls: Type[T], rich_text: RichText, name: str | None = None) -> T:
        return cls(name=name or cls.PROP_NAME, rich_text=rich_text)

    @classmethod
    def empty(cls: Type[T], name: str | None = None) -> T:
        return cls(
            name=name or cls.PROP_NAME,
            rich_text=RichText.empty(),
        )

    @property
    def text(self) -> str:
        return self.rich_text.to_plain_text()

    @property
    def _prop_type(self) -> Prop:
        return Prop.RICH_TEXT

    @property
    def _value_for_filter(self) -> Any:
        return self.text
