from abc import ABCMeta, abstractmethod
from datetime import date
from typing import Any
import json


class RichTextElement(metaclass=ABCMeta):
    annotations: dict[str, bool] | None
    plain_text: str | None
    href: dict[str, bool] | None

    def __init__(
        self,
        annotations: dict[str, bool] | None = None,
        plain_text: str | None = None,
        href: dict[str, bool] | None = None,
    ) -> None:
        self.annotations = annotations
        self.plain_text = plain_text
        self.href = href

    def to_dict(self) -> dict:
        result = {
            "type": self.get_type(),
        }
        if self.annotations is not None:
            result["annotations"] = self.annotations
        if self.plain_text is not None:
            result["plain_text"] = self.plain_text
        if self.href is not None:
            result["href"] = self.href
        result[self.get_type()] = self.to_dict_sub()
        return result

    @abstractmethod
    def to_slack_text(self) -> str:
        pass

    @staticmethod
    def from_entity(rich_text_element: dict) -> "RichTextElement":  # noqa: C901
        """dictからRichTextElementを生成する"""
        type = rich_text_element["type"]
        if type == "text":
            text = rich_text_element["text"]
            return RichTextTextElement(
                content=text["content"],
                link_url=text["link"]["url"] if text.get("link") else None,
                annotations=rich_text_element["annotations"],
                plain_text=rich_text_element["plain_text"],
                href=rich_text_element["href"],
            )
        if type == "mention":
            mention = rich_text_element["mention"]
            mention_type = mention["type"]
            if mention_type in ["database", "page"]:
                return RichTextMentionElement(
                    mention_type=mention_type,
                    object_id=mention[mention_type]["id"],
                    annotations=rich_text_element["annotations"],
                    plain_text=rich_text_element["plain_text"],
                    href=rich_text_element["href"],
                )
            if mention_type == "date":
                return RichTextMentionElement(
                    mention_type=mention_type,
                    start_date=mention["date"]["start"],
                    end_date=mention["date"]["end"],
                    annotations=rich_text_element["annotations"],
                    plain_text=rich_text_element["plain_text"],
                    href=rich_text_element["href"],
                )
            if mention_type == "link_preview":
                return RichTextMentionElement(
                    mention_type=mention_type,
                    link_preview_url=mention["link_preview"]["url"],
                    annotations=rich_text_element["annotations"],
                    plain_text=rich_text_element["plain_text"],
                    href=rich_text_element["href"],
                )
            if mention_type == "link_mention":
                return RichTextMentionElement(
                    mention_type=mention_type,
                    link_mention=mention["link_mention"],
                    annotations=rich_text_element["annotations"],
                    plain_text=rich_text_element["plain_text"],
                    href=rich_text_element["href"],
                )
            raise Exception(f"invalid mention_type: {mention_type} {json.dumps(rich_text_element, ensure_ascii=False)}")
        if type == "equation":
            raise NotImplementedError("equation is not implemented yet")
        raise Exception("invalid type")

    @abstractmethod
    def to_plain_text(self) -> str:
        """plain_textに変換する"""

    @abstractmethod
    def get_type(self) -> str:
        """text, mention, equationのどれかを返す"""

    @abstractmethod
    def to_dict_sub(self) -> str:
        """Text, Mention, Equationのそれぞれで実装する"""


class RichTextTextElement(RichTextElement):
    content: str
    link_url: str | None = None

    def __init__(
        self,
        content: str,
        link_url: str | None = None,
        annotations: dict[str, bool] | None = None,
        plain_text: str | None = None,
        href: dict[str, bool] | None = None,
    ) -> None:
        self.content = content
        self.link_url = link_url
        super().__init__(annotations, plain_text, href)

    @staticmethod
    def of(content: str, link_url: str | None = None) -> "RichTextTextElement":
        return RichTextTextElement(
            content=content,
            link_url=link_url,
        )

    def to_slack_text(self) -> str:
        return self.content

    def to_plain_text(self) -> str:
        return self.content

    def get_type(self) -> str:
        return "text"

    def to_dict_sub(self) -> str:
        result = {
            "content": self.content,
        }
        if self.link_url is not None:
            result["link"] = {
                "url": self.link_url,
            }
        return result


class RichTextMentionElement(RichTextElement):
    # TODO: 日付やリンクプレビューなどもあるみたい
    # refs: https://developers.notion.com/reference/rich-text#mention
    mention_type: str  # database, page, date, link_preview
    object_id: str | None  # database,pageのどちらかで利用。database_idまたはpage_id
    start_date: str | None = None  # dateのみ利用
    end_date: str | None = None  # dateのみ利用
    link_preview_url: str | None = None  # link_previewのみ利用
    mentioned_href: str | None = None  # link_mentionのみ利用

    def __init__(
        self,
        mention_type: str,
        object_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        link_preview_url: str | None = None,
        link_mention: dict[str, Any] | None = None,
        annotations: dict[str, bool] | None = None,
        plain_text: str | None = None,
        href: dict[str, bool] | None = None,
    ) -> None:
        self.mention_type = mention_type
        self.object_id = object_id
        self.start_date = start_date
        self.end_date = end_date
        self.link_preview_url = link_preview_url
        self.link_mention = link_mention
        super().__init__(annotations, plain_text, href)

    @classmethod
    def from_page_type(cls, page_id: str) -> "RichTextMentionElement":
        return cls(mention_type="page", object_id=page_id)

    def to_slack_text(self) -> str:
        # TODO: メンションの場合、そのタイトルは再度クライアントを使ってretrieveしないといけない
        # これをどうするか迷うけど、とりあえず空文字で返す
        return self.to_plain_text()

    def to_plain_text(self) -> str:
        text = self.plain_text if self.mention_type != "link_mention" else self.link_mention["title"]
        return text if text is not None else ""

    @staticmethod
    def of_database(database_id: str) -> "RichTextMentionElement":
        return RichTextMentionElement(
            mention_type="database",
            object_id=database_id,
        )

    @staticmethod
    def of_page(page_id: str) -> "RichTextMentionElement":
        return RichTextMentionElement(
            mention_type="page",
            object_id=page_id,
        )

    @staticmethod
    def of_date(start: date, end: date | None = None) -> "RichTextMentionElement":
        return RichTextMentionElement(
            mention_type="date",
            start_date=start.isoformat(),
            end_date=end.isoformat() if end is not None else None,
        )

    def get_type(self) -> str:
        return "mention"

    def to_dict_sub(self) -> dict:
        """Text, Mention, Equationのそれぞれで実装する"""
        result: dict[str, Any] = {
            "type": self.mention_type,
        }
        if self.link_mention is not None:
            result["link_mention"] = self.link_mention
        if self.mention_type in ["database", "page"]:
            result[self.mention_type] = {
                "id": self.object_id,
            }
        if self.mention_type == "date":
            result["date"] = {
                "start": self.start_date,
            }
            if self.end_date is not None:
                result["date"]["end"] = self.end_date

        return result


class RichTextEquationElement(RichTextElement):
    # TODO: not implemented yet
    pass
