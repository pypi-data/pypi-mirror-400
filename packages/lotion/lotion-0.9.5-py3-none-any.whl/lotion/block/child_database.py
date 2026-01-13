from .block import Block


class ChildDatabase(Block):
    database_name: str

    def __init__(
        self,
        id: str,
        archived: bool,
        created_time: str,
        last_edited_time: str,
        has_children: bool,
        parent: dict,
        database_name: str,
    ):
        super().__init__(
            id, archived, created_time, last_edited_time, has_children, parent
        )
        self.database_name = database_name

    @staticmethod
    def of(block: dict) -> "ChildDatabase":
        database_name = block["child_database"]["title"]
        return ChildDatabase(
            id=block["id"],
            archived=block["archived"],
            created_time=block["created_time"],
            last_edited_time=block["last_edited_time"],
            has_children=block["has_children"],
            parent=block["parent"],
            database_name=database_name,
        )

    @property
    def type(self) -> str:
        return "child_database"

    def to_dict_sub(self) -> dict:
        raise NotImplementedError

    def to_slack_text(self) -> str:
        raise ""
