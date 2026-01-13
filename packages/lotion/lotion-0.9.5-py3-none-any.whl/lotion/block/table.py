from .block import Block


class Table(Block):
    table_width: int
    has_column_header: bool
    has_row_header: bool

    def __init__(
        self,
        table_width: int,
        has_column_header: bool,
        has_row_header: bool,
        id: str,
        archived: bool,
        created_time: str,
        last_edited_time: str,
        has_children: bool,
        parent: dict,
    ):
        super().__init__(
            id, archived, created_time, last_edited_time, has_children, parent
        )
        self.table_width = table_width
        self.has_column_header = has_column_header
        self.has_row_header = has_row_header

    @staticmethod
    def of(block: dict) -> "Table":
        table = block["table"]
        table_width = table["table_width"]
        has_column_header = table["has_column_header"]
        has_row_header = table["has_row_header"]
        return Table(
            id=block["id"],
            archived=block["archived"],
            created_time=block["created_time"],
            last_edited_time=block["last_edited_time"],
            has_children=block["has_children"],
            parent=block["parent"],
            table_width=table_width,
            has_column_header=has_column_header,
            has_row_header=has_row_header,
        )

    @property
    def type(self) -> str:
        return "table"

    def to_dict_sub(self) -> dict:
        raise NotImplementedError

    def to_slack_text(self) -> str:
        return ""
