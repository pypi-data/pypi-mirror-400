from .block import Block


class Bookmark(Block):
    caption: list
    bookmark_url: str

    def __init__(  # noqa: PLR0913
        self,
        bookmark_url: str,
        caption: list | None = None,
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
        self.bookmark_url = bookmark_url
        self.caption = caption or []

    @staticmethod
    def of(block: dict) -> "Bookmark":
        bookmark = block["bookmark"]
        return Bookmark(
            id=block["id"],
            archived=block["archived"],
            created_time=block["created_time"],
            last_edited_time=block["last_edited_time"],
            has_children=block["has_children"],
            parent=block["parent"],
            caption=bookmark["caption"],
            bookmark_url=bookmark.get("url", ""),
        )

    @staticmethod
    def from_url(url: str) -> "Bookmark":
        return Bookmark(bookmark_url=url)

    @property
    def type(self) -> str:
        return "bookmark"

    def to_dict_sub(self) -> dict:
        return {
            "caption": [],
            "url": self.bookmark_url,
        }

    def to_slack_text(self) -> str:
        return self.bookmark_url
