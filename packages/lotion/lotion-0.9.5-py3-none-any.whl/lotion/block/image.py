from .block import Block
from .rich_text.rich_text import RichText


class Image(Block):
    image_caption: list
    image_type: str
    image_file: dict | None
    image_external: dict | None
    type: str = "image"

    def __init__(
        self,
        image_caption: list,
        image_type: str,
        image_file: dict | None = None,
        image_external: dict | None = None,
        id: str | None = None,  # noqa: A002
        archived: bool | None = None,
        created_time: str | None = None,
        last_edited_time: str | None = None,
        has_children: bool | None = None,
        parent: dict | None = None,
    ):
        super().__init__(
            id, archived, created_time, last_edited_time, has_children, parent
        )
        self.image_caption = image_caption
        self.image_type = image_type
        self.image_file = image_file
        self.image_external = image_external

    @staticmethod
    def of(block: dict) -> "Image":
        image = block["image"]
        image_caption = image.get("caption", [])
        image_type = image.get("type", "")
        image_file = image.get("file")
        image_external = image.get("external")
        return Image(
            id=block["id"],
            archived=block["archived"],
            created_time=block["created_time"],
            last_edited_time=block["last_edited_time"],
            has_children=block["has_children"],
            parent=block["parent"],
            image_caption=image_caption,
            image_type=image_type,
            image_file=image_file,
            image_external=image_external,
        )

    def to_dict_sub(self) -> dict:
        if self.image_type == "file":
            msg = "fileタイプは未実装"
            raise NotImplementedError(msg)
        if self.image_type == "external":
            return {
                "caption": self.image_caption,
                "type": self.image_type,
                "external": self.image_external,
            }
        msg = f"Invalid image type: {self.image_type}"
        raise ValueError(msg)

    def to_slack_text(self) -> str:
        if self.image_type == "file":
            return self.image_file["url"]
        if self.image_type == "external":
            return self.image_external["url"]
        msg = f"Invalid image type: {self.image_type}"
        raise ValueError(msg)

    @classmethod
    def from_external_url(cls, url: str, alias_url: str | None = None) -> "Image":
        image_caption = []
        if alias_url:
            image_caption = RichText.from_plain_link(alias_url, alias_url).to_dict()
        return Image(
            image_caption=image_caption,
            image_type="external",
            image_external={"url": url},
        )
