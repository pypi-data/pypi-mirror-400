from dataclasses import dataclass
from typing import Any, Type, TypeVar

from .prop import Prop
from .property import Property

T = TypeVar("T", bound="Email")


@dataclass
class Email(Property):
    """Email class

    ex.
    {'id': 'Io%7C%3A', 'type': 'email', 'email': 'sample@example.com'}
    """

    value: str
    TYPE: str = "email"

    def __init__(
        self,
        name: str,
        value: str = "",
        id: str | None = None,  # noqa: A002
    ) -> None:
        self.name = name
        self.value = value
        self.id = id

    @classmethod
    def of(cls: Type[T], key: str, param: dict) -> T:
        value = param.get("email")
        if value is not None and not isinstance(value, str):
            raise ValueError(f"email must be str, but got {type(value)}")
        return cls(id=param["id"], name=key, value=value or "")

    @classmethod
    def from_email(cls: Type[T], email: str, name: str | None = None) -> T:
        return cls(name=name or cls.PROP_NAME, value=email)

    @classmethod
    def empty(cls: Type[T], name: str | None = None) -> T:
        return cls(name=name or cls.PROP_NAME, value="")

    def __dict__(self) -> dict:
        result = {
            "type": self.TYPE,
            "email": None if self.value == "" else self.value,
        }
        if self.id is not None:
            result["id"] = self.id
        return {
            self.name: result,
        }

    @property
    def _prop_type(self) -> Prop:
        raise NotImplementedError(f"{self.__class__.__name__} doesn't need a property type")

    @property
    def _value_for_filter(self) -> Any:  # noqa: ANN201
        raise NotImplementedError(f"{self.__class__.__name__} doesn't need a value for filter")
