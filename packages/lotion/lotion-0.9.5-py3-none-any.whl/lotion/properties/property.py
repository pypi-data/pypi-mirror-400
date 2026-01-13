from abc import ABCMeta, abstractmethod

from .prop import Prop


class Property(metaclass=ABCMeta):
    id: str | None
    name: str
    TYPE: str = "Property"  # Must be overridden
    PROP_NAME: str = "Property"  # Must be overridden

    @abstractmethod
    def __dict__(self) -> dict:
        pass

    @property
    @abstractmethod
    def _prop_type(self) -> Prop:
        pass

    @property
    @abstractmethod
    def _value_for_filter(self):  # noqa: ANN201
        pass
