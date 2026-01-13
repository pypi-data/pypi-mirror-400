from datetime import date
from typing import Optional
from dataclasses import dataclass
from lotion.block.rich_text.rich_text_element import RichTextElement, RichTextTextElement, RichTextMentionElement
from lotion.block.rich_text.rich_text import RichText


@dataclass(frozen=True)
class RichTextBuilder:
    rich_text: list[RichTextElement]

    @staticmethod
    def get_instance() -> "RichTextBuilder":
        return RichTextBuilder(rich_text=[])

    @staticmethod
    def create() -> "RichTextBuilder":
        return RichTextBuilder(rich_text=[])

    def add_text(self, content: str, link_url: Optional[str] = None) -> "RichTextBuilder":
        self.rich_text.append(RichTextTextElement.of(content, link_url))
        return self

    def add_page_mention(self, page_id: str) -> "RichTextBuilder":
        self.rich_text.append(RichTextMentionElement.of_page(page_id=page_id))
        return self

    def add_date_mention(self, start: date, end: date | None = None) -> "RichTextBuilder":
        self.rich_text.append(RichTextMentionElement.of_date(start=start, end=end))
        return self

    def add_rich_text(self, rich_text: RichText) -> "RichTextBuilder":
        self.rich_text.extend(rich_text.elements)
        return self

    def build(self) -> RichText:
        return RichText(elements=self.rich_text)
