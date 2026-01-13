from dataclasses import dataclass
from typing import Type, TypeVar

from .property import Property

T = TypeVar("T", bound="Rollup")


@dataclass
class Rollup(Property):
    """Rollup class

    ex.
    {'id': '%3BXyX', 'type': 'rollup', 'rollup': {'type': 'number', 'number': 0, 'function': 'count_values'}}
    """

    _rollup: dict
    TYPE: str = "rollup"

    def __init__(
        self,
        name: str,
        rollup: dict = {},
        id: str | None = None,  # noqa: A002
    ) -> None:
        self.name = name
        self._rollup = rollup
        self.id = id

    @classmethod
    def of(cls: Type[T], key: str, param: dict) -> T:
        return cls(
            id=param["id"],
            name=key,
            rollup=param["rollup"],
        )

    @property
    def value(self) -> dict:
        rollup_type = self._rollup["type"]
        return self._rollup[rollup_type]

    def __dict__(self) -> dict:
        raise NotImplementedError("this dict method must not be called")

    @property
    def _prop_type(self):
        raise ValueError(f"{self.__class__.__name__} doesn't need a property type")

    @property
    def _value_for_filter(self):
        raise ValueError(f"{self.__class__.__name__} doesn't need a value for filter")
