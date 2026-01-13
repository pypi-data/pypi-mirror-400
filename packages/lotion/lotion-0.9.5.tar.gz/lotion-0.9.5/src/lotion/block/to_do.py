from .block import Block
from .rich_text.rich_text import RichText


class ToDo(Block):
    rich_text: RichText
    color: str
    checked: bool

    def __init__(
        self,
        rich_text: RichText,
        color: str | None = None,
        checked: bool | None = None,
        id: str | None = None,
        archived: bool | None = None,
        created_time: str | None = None,
        last_edited_time: str | None = None,
        has_children: bool | None = None,
        parent: dict | None = None,
    ):
        super().__init__(
            id, archived, created_time, last_edited_time, has_children, parent
        )
        self.rich_text = rich_text
        self.color = color
        self.checked = checked or False

    @staticmethod
    def of(block: dict) -> "ToDo":
        to_do = block["to_do"]
        rich_text = RichText.from_entity(to_do["rich_text"])
        return ToDo(
            id=block["id"],
            archived=block["archived"],
            created_time=block["created_time"],
            last_edited_time=block["last_edited_time"],
            has_children=block["has_children"],
            parent=block["parent"],
            rich_text=rich_text,
            color=to_do["color"],
            checked=to_do["checked"],
        )

    @staticmethod
    def from_plain_text(text: str, checked: bool | None = None) -> "ToDo":
        checked = checked or False
        return ToDo(rich_text=RichText.from_plain_text(text), checked=checked)

    @property
    def type(self) -> str:
        return "to_do"

    def to_dict_sub(self) -> dict:
        result = {
            "rich_text": self.rich_text.to_dict(),
            "checked": self.checked,
        }
        if self.color is not None:
            result["color"] = self.color
        return result

    def to_slack_text(self) -> str:
        return (
            "[ ] " + self.rich_text.to_slack_text()
            if not self.checked
            else "[x] " + self.rich_text.to_slack_text()
        )
