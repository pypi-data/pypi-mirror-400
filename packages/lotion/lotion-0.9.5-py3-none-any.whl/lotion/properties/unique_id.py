from dataclasses import dataclass
from typing import Type, TypeVar

from .property import Property

T = TypeVar("T", bound="UniqueId")


@dataclass
class UniqueId(Property):
    """UniqueId class

    ex.
    {'id': 'vI%3FY', 'type': 'unique_id', 'unique_id': {'prefix': None, 'number': 1}}
    """

    prefix: str | None
    number: int
    TYPE: str = "unique_id"

    def __init__(
        self,
        name: str,
        number: int,
        id: str,
        prefix: str | None = None,
    ) -> None:
        self.name = name
        self.prefix = prefix
        self.number = number
        self.id = id

    @classmethod
    def of(cls: Type[T], key: str, param: dict) -> T:
        return cls(
            id=param["id"],
            name=key,
            prefix=param["unique_id"]["prefix"],
            number=param["unique_id"]["number"],
        )

    def __dict__(self) -> dict:
        raise NotImplementedError("this dict method must not be called")

    @property
    def _prop_type(self):
        raise ValueError(f"{self.__class__.__name__} doesn't need a property type")

    @property
    def _value_for_filter(self):
        raise ValueError(f"{self.__class__.__name__} doesn't need a value for filter")
