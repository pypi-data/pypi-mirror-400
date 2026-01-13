from .block import Block


class Divider(Block):
    def __init__(
        self,
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

    @staticmethod
    def of(block: dict) -> "Divider":
        return Divider(
            id=block["id"],
            archived=block["archived"],
            created_time=block["created_time"],
            last_edited_time=block["last_edited_time"],
            has_children=block["has_children"],
            parent=block["parent"],
        )

    @property
    def type(self) -> str:
        return "divider"

    def to_dict_sub(self) -> dict:
        return {}

    def to_slack_text(self) -> str:
        return "---"
