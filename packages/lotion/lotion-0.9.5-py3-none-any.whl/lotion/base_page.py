from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Type, TypeVar, cast

from .datetime_utils import JST
from .properties.files import Files
from .property_translator import PropertyTranslator
from .base_operator import BaseOperator
from .block.block import Block
from .page.page_id import PageId
from .properties.checkbox import Checkbox
from .properties.cover import Cover
from .properties.date import Date
from .properties.email import Email
from .properties.formula import Formula
from .properties.icon import Icon
from .properties.multi_select import MultiSelect
from .properties.number import Number
from .properties.phone_number import PhoneNumber
from .properties.properties import Properties
from .properties.property import Property
from .properties.relation import Relation
from .properties.rollup import Rollup
from .properties.select import Select
from .properties.status import Status
from .properties.text import Text
from .properties.title import Title
from .properties.unique_id import UniqueId
from .properties.url import Url

T = TypeVar("T", bound="BasePage")

P = TypeVar("P", bound=Property)


class NotCreatedError(Exception):
    pass


class NotFoundPropertyError(Exception):
    def __init__(self, class_name: str, prop_name: str):
        super().__init__(f"{class_name} property not found. name: {prop_name}")


@dataclass
class BasePage:
    properties: Properties
    block_children: list[Block] = field(default_factory=list)
    id_: str | None = None
    url_: str | None = None
    created_time: datetime | None = None
    last_edited_time: datetime | None = None
    _created_by: BaseOperator | None = None
    _last_edited_by: BaseOperator | None = None
    cover: Cover | None = None
    icon: Icon | None = None
    archived: bool | None = False
    parent: dict | None = None
    object = "page"
    DATABASE_ID: str = "database_id"  # must be set in subclass

    @classmethod
    def create(
        cls: Type[T],
        properties: list[Property] | None = None,
        blocks: list[Block] | None = None,
        cover: Cover | None = None,
        icon: Icon | None = None,
    ) -> T:
        return cls(
            id_=None,
            url_=None,
            created_time=None,
            last_edited_time=None,
            _created_by=None,
            _last_edited_by=None,
            properties=Properties(values=properties or []),
            cover=cover,
            icon=icon,
            archived=False,
            parent=None,
            block_children=blocks or [],
        )

    def get_slack_text_in_block_children(self) -> str:
        # FIXME: block_childrenをBlocks型にしたうえで、メソッドをBlocksに移動する
        if not self.block_children or len(self.block_children) == 0:
            return ""
        return "\n".join([block.to_slack_text() for block in self.block_children])

    def get_title(self) -> Title:
        return self.properties.get_title()

    def get_title_text(self) -> str:
        return self.get_title().rich_text.to_plain_text()

    @property
    def created_at(self) -> datetime:
        if self.created_time is None:
            raise NotCreatedError("created_at is None.")
        return self.created_time

    @property
    def updated_at(self) -> datetime:
        if self.last_edited_time is None:
            raise NotCreatedError("created_at is None.")
        return self.last_edited_time

    def get_prop(self, instance_class: Type[P]) -> P:
        parent_class = self.__get_parent_class(instance_class)
        if parent_class not in [
            Checkbox,
            Date,
            Email,
            MultiSelect,
            Number,
            PhoneNumber,
            Relation,
            Select,
            Status,
            Text,
            Title,
            Url,
        ]:
            error_message = "instance_class must be one of the following classes: Checkbox, Date, Email, MultiSelect, \
                Number, PhoneNumber, Relation, Select, Status, Text, Title, Url"
            raise ValueError(error_message)
        result = self.properties.get_property(name=instance_class.PROP_NAME, instance_class=parent_class)
        if result is None:
            raise NotFoundPropertyError(class_name=instance_class.__name__, prop_name=instance_class.PROP_NAME)
        return cast(P, result)

    def __get_parent_class(self, instance_class: Type[P]) -> Type[P]:
        parent_classes = instance_class.__bases__
        if not parent_classes:
            return instance_class
        return parent_classes[0]

    def set_prop(self, value: Property) -> None:
        self.properties = self.properties.append_property(value)

    def get_status(self, name: str) -> Status:
        return self._get_property(name=name, instance_class=Status)  # type: ignore

    def get_text(self, name: str) -> Text:
        return self._get_property(name=name, instance_class=Text)  # type: ignore

    def get_date(self, name: str) -> Date:
        return self._get_property(name=name, instance_class=Date)  # type: ignore

    def get_select(self, name: str) -> Select:
        return self._get_property(name=name, instance_class=Select)  # type: ignore

    def get_multi_select(self, name: str) -> MultiSelect:
        return self._get_property(name=name, instance_class=MultiSelect)  # type: ignore

    def get_relation(self, name: str) -> Relation:
        return self._get_property(name=name, instance_class=Relation)  # type: ignore

    def get_checkbox(self, name: str) -> Checkbox:
        return self._get_property(name=name, instance_class=Checkbox)  # type: ignore

    def get_url(self, name: str) -> Url:
        return self._get_property(name=name, instance_class=Url)  # type: ignore

    def get_number(self, name: str) -> Number:
        return self._get_property(name=name, instance_class=Number)  # type: ignore

    def get_email(self, name: str) -> Email:
        return self._get_property(name=name, instance_class=Email)  # type: ignore

    def get_phone_number(self, name: str) -> PhoneNumber:
        return self._get_property(name=name, instance_class=PhoneNumber)  # type: ignore

    def get_formula(self, name: str) -> Formula:
        return self._get_property(name=name, instance_class=Formula)  # type: ignore

    def get_rollup(self, name: str) -> Rollup:
        return self._get_property(name=name, instance_class=Rollup)  # type: ignore

    def get_unique_id(self, name: str) -> UniqueId:
        return self._get_property(name=name, instance_class=UniqueId)  # type: ignore

    def get_files(self, name: str) -> Files:
        return self._get_property(name=name, instance_class=Files)  # type: ignore

    def _get_property(self, name: str, instance_class: type) -> Property:
        result = self.properties.get_property(name=name, instance_class=instance_class)
        if result is None:
            raise NotFoundPropertyError(class_name=instance_class.__name__, prop_name=name)
        return result

    def get_parant_database_id(self) -> str | None:
        """未実装。削除すべきかも"""
        if self.parent is None or "database_id" not in self.parent:
            return None
        return self.parent["database_id"]

    def update_id_and_url(self, page_id: str, url: str) -> None:
        self.id_ = page_id
        self.url_ = url

    def title_for_slack(self) -> str:
        """Slackでの表示用のリンクつきタイトルを返す"""
        return f"<{self.url}|{self.get_title_text()}>"

    def copy(self):
        """コピーを作成する。新しいページになる"""
        cls = self.__class__
        return cls.create(properties=self.properties.values, blocks=self.block_children)

    def title_for_markdown(self) -> str:
        """Markdownでの表示用のリンクつきタイトルを返す"""
        return f"[{self.get_title_text()}]({self.url})"

    @property
    def id(self) -> str:
        if self.id_ is None:
            raise NotCreatedError("id is None.")
        return PageId(self.id_).value

    @property
    def url(self) -> str:
        if self.url_ is None:
            raise NotCreatedError("url is None.")
        return self.url_

    def is_created(self) -> bool:
        return self.id_ is not None

    def get_id_and_url(self) -> dict[str, str]:
        return {
            "id": self.id,
            "url": self.url,
        }

    @property
    def created_by(self) -> BaseOperator:
        if self._created_by is None:
            raise NotCreatedError("created_by is None.")
        return self._created_by

    @property
    def edited_by(self) -> BaseOperator:
        if self._last_edited_by is None:
            raise NotCreatedError("created_by is None.")
        return self._last_edited_by

    @classmethod
    def from_data(cls: Type[T], data: dict, block_children: list[Block] | None = None) -> T:
        id_ = PageId(data["id"]).value if data["id"] is not None else None
        url_ = data["url"] if "url" in data else None
        created_time = datetime.fromisoformat(data["created_time"]) + timedelta(hours=9)
        last_edited_time = datetime.fromisoformat(data["last_edited_time"]) + timedelta(hours=9)
        created_by = BaseOperator.of(data["created_by"])
        last_edited_by = BaseOperator.of(data["last_edited_by"])
        cover = Cover.of(data["cover"]) if data["cover"] is not None else None
        icon = Icon.of(data["icon"]) if data["icon"] is not None else None
        archived = data["archived"]
        properties = PropertyTranslator.from_dict(data["properties"])
        block_children = block_children or []

        return cls(
            id_=id_,
            url_=url_,
            created_time=created_time.replace(tzinfo=JST),
            last_edited_time=last_edited_time.replace(tzinfo=JST),
            _created_by=created_by,
            _last_edited_by=last_edited_by,
            cover=cover,
            icon=icon,
            archived=archived,
            properties=properties,
            block_children=block_children,
        )

    @classmethod
    def _get_database_id(cls) -> str:
        result = cls.DATABASE_ID
        if result is None:
            raise ValueError("DATABASE_ID is null")
        return result

    def _get_own_database_id(self) -> str:
        return self.__class__._get_database_id()
