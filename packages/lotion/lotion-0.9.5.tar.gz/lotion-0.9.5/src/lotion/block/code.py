from .block import Block
from .rich_text.rich_text import RichText


class Code(Block):
    def __init__(  # noqa: PLR0913
        self,
        rich_text: RichText,
        language: str | None = None,
        id: str | None = None,  # noqa: A002
        archived: bool | None = None,
        created_time: str | None = None,
        last_edited_time: str | None = None,
        has_children: bool | None = None,
        parent: dict | None = None,
    ) -> None:
        super().__init__(
            id, archived, created_time, last_edited_time, has_children, parent
        )
        self.rich_text = rich_text
        self.language = language

    @staticmethod
    def of(block: dict) -> "Code":
        code = block["code"]
        rich_text = RichText.from_entity(code["rich_text"])
        language = code.get("language")
        return Code(
            rich_text=rich_text,
            language=language,
            id=block["id"],
            archived=block["archived"],
            created_time=block["created_time"],
            last_edited_time=block["last_edited_time"],
            has_children=block["has_children"],
            parent=block["parent"],
        )

    @staticmethod
    def from_plain_text(text: str, language: str | None = None) -> "Code":
        rich_text = RichText.from_plain_text(text)
        return Code(rich_text=rich_text, language=language)

    @property
    def type(self) -> str:
        return "code"

    def to_dict_sub(self) -> dict:
        return {
            "rich_text": self.rich_text.to_dict(),
            "language": self.language,
        }

    def to_slack_text(self) -> str:
        language = self.language or ""
        return f"```{language}\n{self.rich_text.to_plain_text()}\n```"
