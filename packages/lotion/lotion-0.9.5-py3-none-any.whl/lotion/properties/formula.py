from dataclasses import dataclass
from typing import Type, TypeVar

from .property import Property

T = TypeVar("T", bound="Formula")


@dataclass
class Formula(Property):
    """Formula class

    ex.
    {'id': 'h_pG', 'type': 'formula', 'formula': {'type': 'number', 'number': 50}}
    """

    _formula: dict
    TYPE: str = "formula"

    def __init__(
        self,
        name: str,
        formula: dict = {},
        id: str | None = None,  # noqa: A002
    ) -> None:
        self.name = name
        self._formula = formula
        self.id = id

    @classmethod
    def of(cls: Type[T], key: str, param: dict) -> T:
        return cls(
            id=param["id"],
            name=key,
            formula=param["formula"],
        )

    @property
    def value(self) -> dict:
        formula_type = self._formula["type"]
        return self._formula[formula_type]

    def __dict__(self) -> dict:
        raise NotImplementedError("this dict method must not be called")

    @property
    def _prop_type(self):
        raise ValueError(f"{self.__class__.__name__} doesn't need a property type")

    @property
    def _value_for_filter(self):
        raise ValueError(f"{self.__class__.__name__} doesn't need a value for filter")
