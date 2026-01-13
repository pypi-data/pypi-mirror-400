from abc import ABCMeta, abstractmethod
from dataclasses import dataclass


@dataclass
class Block(metaclass=ABCMeta):
    id: str | None
    archived: bool | None
    has_children: bool | None
    created_time: str | None
    last_edited_time: str | None
    parent: dict[str, str] | None = None

    def to_dict(self, for_create: bool|None = None) -> dict:
        result = {
            "object": "block",
        }
        if not for_create:
            if self.id is not None:
                result["id"] = self.id
            if self.archived is not None:
                result["archived"] = self.archived
            if self.has_children is not None:
                result["has_children"] = self.has_children
            if self.created_time is not None:
                result["created_time"] = self.created_time
            if self.last_edited_time is not None:
                result["last_edited_time"] = self.last_edited_time
            if self.parent is not None:
                result["parent"] = self.parent
        result["type"] = self.type
        result[self.type] = self.to_dict_sub()
        return result

    @abstractmethod
    def to_dict_sub(self) -> dict:
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        pass

    @abstractmethod
    def to_slack_text(self) -> str:
        pass
