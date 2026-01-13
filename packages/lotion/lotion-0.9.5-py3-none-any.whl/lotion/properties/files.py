from dataclasses import dataclass
from typing import Type, TypeVar

from .property import Property

T = TypeVar("T", bound="Files")


@dataclass(frozen=True)
class File:
    """File class"""

    name: str
    url: str
    expired_at: str | None = None

    @staticmethod
    def of(param: dict) -> "File":
        name = param["name"]
        type_ = param["type"]
        url = param[type_]["url"]
        expired_at = param[type_]["expiry_time"] if type_ == "file" else None
        return File(
            name=name,
            url=url,
            expired_at=expired_at,
        )


@dataclass
class Files(Property):
    """Files class

    ex.
    {'id': '%7BjJx', 'type': 'files', 'files': []}
    """

    _files: list
    TYPE: str = "files"

    def __init__(
        self,
        name: str,
        files: list = [],
        id: str | None = None,  # noqa: A002
    ) -> None:
        self.name = name
        self._files = files
        self.id = id

    @classmethod
    def of(cls: Type[T], key: str, param: dict) -> T:
        return cls(
            id=param["id"],
            name=key,
            files=param["files"],
        )

    @property
    def value(self) -> list[File]:
        return [File.of(param) for param in self._files]

    def __dict__(self) -> dict:
        raise NotImplementedError("this dict method must not be called")

    @property
    def _prop_type(self):
        raise ValueError(f"{self.__class__.__name__} doesn't need a property type")

    @property
    def _value_for_filter(self):
        raise ValueError(f"{self.__class__.__name__} doesn't need a value for filter")
