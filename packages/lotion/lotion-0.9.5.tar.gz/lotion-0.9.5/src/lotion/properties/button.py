from dataclasses import dataclass
from typing import Any, Type, TypeVar

from .property import Property

T = TypeVar("T", bound="Button")


@dataclass
class Button(Property):
    id: str
    name: str
    TYPE: str = "button"

    @classmethod
    def of(cls: Type[T], key: str, property: dict) -> T:
        return cls(id=property["id"], name=key)

    def value_for_filter(self) -> str:
        raise NotImplementedError

    def __dict__(self) -> dict:
        return {
            self.name: {
                "id": self.id,
                "type": self.TYPE,
                "button": {},
            },
        }

    @property
    def _prop_type(self):
        raise ValueError(f"{self.__class__.__name__} doesn't need a property type")

    @property
    def _value_for_filter(self) -> Any:  # noqa: ANN201
        raise ValueError(f"{self.__class__.__name__} doesn't need a value for filter")
