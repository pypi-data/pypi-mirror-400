from dataclasses import dataclass

from lotion.block.rich_text.rich_text_element import RichTextElement, RichTextTextElement


@dataclass(frozen=True)
class RichText:
    elements: list[RichTextElement]

    @staticmethod
    def from_entity(rich_text: list) -> "RichText":
        return RichText(elements=list(map(lambda x: RichTextElement.from_entity(x), rich_text)))

    @staticmethod
    def empty() -> "RichText":
        return RichText(elements=[])

    @staticmethod
    def from_plain_text(text: str) -> "RichText":
        rich_text_element = RichTextTextElement.of(content=text)
        return RichText(elements=[rich_text_element])

    @classmethod
    def from_plain_link(cls, text: str, url: str) -> "RichText":
        rich_text_element = RichTextTextElement.of(content=text, link_url=url)
        return cls(elements=[rich_text_element])

    def to_plain_text(self) -> str:
        return "".join(map(lambda x: x.to_plain_text(), self.elements))

    def to_dict(self) -> list[dict]:
        return list(map(lambda x: x.to_dict(), self.elements))

    def to_slack_text(self) -> str:
        return "".join([x.to_slack_text() for x in self.elements])
