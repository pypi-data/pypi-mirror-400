from dataclasses import dataclass
from typing import Any, Type, TypeVar

from .property import Property

T = TypeVar("T", bound="CreatedBy")


@dataclass
class CreatedBy(Property):
    TYPE: str = "created_by"

    def __init__(
        self,
        name: str,
        created_by_param: dict,
        id: str | None = None,  # noqa: A002
    ) -> None:
        self.name = name
        self.created_by_param = created_by_param
        self.id = id

    @classmethod
    def of(cls: Type[T], key: str, param: dict) -> T:
        return cls(id=param["id"], name=key, created_by_param=param["created_by"])

    def __dict__(self) -> dict[str, Any]:
        return {
            self.name: {
                "id": self.id,
                "type": self.TYPE,
                "created_by": self.created_by_param,
            },
        }

    def value_for_filter(self) -> str:
        raise NotImplementedError()

    @property
    def _prop_type(self):
        raise ValueError(f"{self.__class__.__name__} doesn't need a property type")

    @property
    def _value_for_filter(self):
        raise ValueError(f"{self.__class__.__name__} doesn't need a value for filter")
