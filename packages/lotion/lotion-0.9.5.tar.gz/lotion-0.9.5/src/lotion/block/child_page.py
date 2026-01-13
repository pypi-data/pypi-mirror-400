from .block import Block


class ChildPage(Block):
    title: str

    def __init__(
        self,
        id: str,
        archived: bool,
        created_time: str,
        last_edited_time: str,
        has_children: bool,
        parent: dict,
        title: str,
    ):
        super().__init__(
            id, archived, created_time, last_edited_time, has_children, parent
        )
        self.title = title

    @staticmethod
    def of(block: dict) -> "ChildPage":
        title = block["child_page"]["title"]
        return ChildPage(
            id=block["id"],
            archived=block["archived"],
            created_time=block["created_time"],
            last_edited_time=block["last_edited_time"],
            has_children=block["has_children"],
            parent=block["parent"],
            title=title,
        )

    @property
    def type(self) -> str:
        return "child_page"

    def to_dict_sub(self) -> dict:
        raise NotImplementedError

    def to_slack_text(self) -> str:
        return ""
