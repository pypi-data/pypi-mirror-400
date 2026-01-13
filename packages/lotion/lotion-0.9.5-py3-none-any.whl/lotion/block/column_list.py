from .block import Block


class ColumnList(Block):
    column_list: dict
    type: str = "column_list"

    def __init__(  # noqa: PLR0913
        self,
        column_list: dict,
        id: str | None = None,  # noqa: A002
        archived: bool | None = None,
        created_time: str | None = None,
        last_edited_time: str | None = None,
        has_children: bool | None = None,
        parent: dict | None = None,
    ) -> None:
        super().__init__(
            id, archived, has_children, created_time, last_edited_time, parent
        )
        self.column_list = column_list

    @staticmethod
    def of(block: dict) -> "ColumnList":
        column_list = block["column_list"]
        return ColumnList(
            id=block["id"],
            archived=block["archived"],
            created_time=block["created_time"],
            last_edited_time=block["last_edited_time"],
            has_children=block["has_children"],
            parent=block["parent"],
            column_list=column_list,
        )

    def to_dict_sub(self) -> dict:
        return {
            "column_list": self.column_list,
        }

    def to_slack_text(self) -> str:
        return ""
