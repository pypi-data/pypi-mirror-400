from dataclasses import dataclass
from typing import Any, Type, TypeVar

from .prop import Prop
from .property import Property

T = TypeVar("T", bound="Select")


@dataclass
class Select(Property):
    selected_name: str
    selected_id: str | None
    selected_color: str | None
    TYPE: str = "select"

    def __init__(
        self,
        name: str,
        selected_name: str = "",
        selected_id: str | None = None,
        selected_color: str | None = None,
        id: str | None = None,
    ):
        self.name = name
        self.id = id
        self.selected_name = selected_name
        self.selected_id = selected_id
        self.selected_color = selected_color

    @classmethod
    def of(cls: Type[T], name: str, param: dict) -> T:
        select = param["select"]
        if select is None:
            return cls(name=name)
        return cls(
            name=name,
            selected_id=select["id"],
            selected_name=select["name"],
            selected_color=select["color"],
            id=param["id"],
        )

    @classmethod
    def empty(cls: Type[T], name: str | None = None) -> T:
        return cls(name=name or cls.PROP_NAME)

    @classmethod
    def from_name(cls: Type[T], selected_name: str, name: str | None = None) -> T:
        return cls(name=name or cls.PROP_NAME, selected_name=selected_name)

    def _is_set_name_only(self) -> bool:
        """selected_idが指定されていない場合にTrueを返す。このときは一度Selectを取得しなおす必要がある。"""
        return self.selected_id is None and self.selected_name != ""

    def is_empty(self) -> bool:
        return self.selected_name == ""

    def __dict__(self):
        if self.is_empty():
            # 空の場合はtypeだけ返す
            return {
                self.name: {
                    "type": self.TYPE,
                    "select": None,
                }
            }
        result = {
            "type": self.TYPE,
            "select": {
                "id": self.selected_id,
                "name": self.selected_name,
                "color": self.selected_color,
            },
        }
        if self.id is not None:
            result["id"] = self.id
        return {self.name: result}

    # __hash__と__eq__を実装することで、リストやセットの中で比較が可能になる
    def __hash__(self):
        return hash(self.selected_id)

    def __eq__(self, other):
        return self.selected_id == other.selected_id

    @property
    def _prop_type(self) -> Prop:
        return Prop.SELECT

    @property
    def _value_for_filter(self) -> Any:
        return self.selected_name


@dataclass(frozen=True)
class Selects:
    values: list[Select]

    def get(self, status_name: str) -> Select:
        for value in self.values:
            if value.selected_name == status_name:
                return value
        raise ValueError(f"Select not found: {status_name}")

    @property
    def size(self) -> int:
        return len(self.values)
