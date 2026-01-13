from .block import Block


class Video(Block):
    caption: list
    external_url: str

    def __init__(
        self,
        external_url: str,
        caption: list,
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
        self.external_url = external_url
        self.caption = caption

    @staticmethod
    def of(block: dict) -> "Video":
        video = block["video"]
        video_external = video["external"] if "external" in video else {}
        return Video(
            id=block["id"],
            archived=block["archived"],
            created_time=block["created_time"],
            last_edited_time=block["last_edited_time"],
            has_children=block["has_children"],
            parent=block["parent"],
            caption=video["caption"],
            external_url=video_external["url"] if "url" in video_external else "",
        )

    @staticmethod
    def from_external_url(url: str) -> "Video":
        return Video(
            external_url=url,
            caption=[],
        )

    @property
    def type(self) -> str:
        return "video"

    def to_dict_sub(self) -> dict:
        return {
            "caption": self.caption,
            "type": "external",
            "external": {"url": self.external_url},
        }

    def to_slack_text(self) -> str:
        return self.external_url
