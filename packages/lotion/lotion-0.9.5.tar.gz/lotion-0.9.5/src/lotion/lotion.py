import os
from datetime import date, datetime
from logging import Logger, getLogger
from typing import Generic, Type, TypeVar

from notion_client import Client
from notion_client.errors import APIResponseError, HTTPResponseError

from .base_page import BasePage
from .block import Block, BlockFactory
from .filter.builder import Builder
from .filter.condition.cond import Cond
from .page.page_id import PageId
from .properties.cover import Cover
from .properties.multi_select import MultiSelect, MultiSelectElement
from .properties.prop import Prop
from .properties.properties import Properties
from .properties.property import Property
from .properties.select import Select
from .properties.text import Text
from .properties.title import Title

NOTION_API_ERROR_BAD_GATEWAY = 502

T = TypeVar("T", bound="BasePage")
S = TypeVar("S", bound=Select)
M = TypeVar("M", bound=MultiSelect)
TI = TypeVar("TI", bound=Title)


class SelectCache(Generic[S]):
    def __init__(self) -> None:
        self.cache: dict[str, S] = {}

    def get(self, key: str) -> S:
        return self.cache[key]

    def set(self, key: str, value: S) -> None:
        self.cache[key] = value

    def has(self, key: str) -> bool:
        return key in self.cache


SELECT_CACHE: dict[str, SelectCache] = {}


class MultiSelectCache:
    def __init__(self) -> None:
        self.cache: dict[str, MultiSelectElement] = {}

    def get(self, key: str) -> MultiSelectElement:
        return self.cache[key]

    def set(self, key: str, value: MultiSelectElement) -> None:
        self.cache[key] = value

    def has(self, key: str) -> bool:
        return key in self.cache


MULTI_SELECT_CACHE: dict[str, MultiSelectCache] = {}


class AppendBlockError(Exception):
    def __init__(self, block_id: str, blocks: list[dict], e: Exception) -> None:
        self.block_id = block_id
        self.blocks = blocks
        self.e = e
        super().__init__(f"block_id: {block_id}, blocks: {blocks}, error: {e}")


class NotionApiError(Exception):
    def __init__(
        self,
        page_id: str | None = None,
        database_id: str | None = None,
        e: APIResponseError | HTTPResponseError | None = None,
        properties: Properties | dict | None = None,
    ) -> None:
        self.database_id = database_id
        self.e = e
        self.properties = properties

        message = ""
        if e is not None:
            message += f", error: {e}"
        if page_id is not None:
            message += f"page_id: {page_id}"
        if database_id is not None:
            message += f"database_id: {database_id}"
        if properties is not None:
            properties_ = properties.__dict__() if isinstance(properties, Properties) else properties
            message += f", properties: {properties_}"
        super().__init__(message)


class Lotion:
    def __init__(self, client: Client, max_retry_count: int = 3, logger: Logger | None = None) -> None:
        self.client = client
        self.max_retry_count = max_retry_count
        self._logger = logger or getLogger(__name__)

    @staticmethod
    def get_instance(
        secret: str | None = None, 
        max_retry_count: int = 3, 
        logger: Logger | None = None,
        notion_version: str = "2022-06-28"
    ) -> "Lotion":
        client = Client(auth=secret or os.getenv("NOTION_SECRET"), notion_version=notion_version)
        return Lotion(client, max_retry_count=max_retry_count, logger=logger)

    def retrieve_page(self, page_id: str, cls: Type[T] = BasePage) -> T:
        """指定されたページを取得する"""
        page_entity = self.__retrieve_page(page_id=page_id)
        return self.__convert_page_model(page_entity=page_entity, include_children=True, cls=cls)

    def update_page(self, page_id: str, properties: list[Property] | None = None) -> None:
        """指定されたページを更新する"""
        update_properties = Properties(values=properties or [])
        self.__update(page_id=page_id, properties=update_properties)

    def update(self, page: T) -> T:
        """ページを更新する"""
        _page = self._convert_to_update_page_object(page)
        if _page.is_created():
            self.__update(page_id=page.id, properties=Properties(values=page.properties.values))
            return _page
        return self.create_page(_page)

    def retrieve_comments(self, page_id: str) -> list[dict]:
        """指定されたページのコメントを取得する"""
        comments = self.client.comments.list(
            block_id=page_id,
        )
        return comments["results"]

    def create_page_in_database(
        self,
        database_id: str,
        cover: Cover | None = None,
        properties: list[Property] | None = None,
        blocks: list[Block] | None = None,
        cls: Type[T] = BasePage,
    ) -> T:
        """データベース上にページを新規作成する"""
        page = self.__create_page(
            database_id=database_id,
            cover=cover.__dict__() if cover is not None else None,
            properties=(
                Properties(values=properties).exclude_for_update().__dict__() if properties is not None else {}
            ),
        )
        if blocks is not None:
            self.append_blocks(block_id=page["id"], blocks=blocks)
        return self.retrieve_page(page_id=page["id"], cls=cls)

    def create_page(self, page: T) -> T:
        """ページを新規作成する"""
        _page = self._convert_to_update_page_object(page)
        return self.create_page_in_database(
            database_id=_page._get_own_database_id(),
            cover=_page.cover,
            properties=_page.properties.values,
            blocks=_page.block_children,
            cls=type(_page),
        )

    def retrieve_database(  # noqa: PLR0913
        self,
        database_id: str,
        filter_param: dict | None = None,
        include_children: bool | None = None,
        cls: Type[T] = BasePage,
    ) -> list[T]:
        """指定されたデータベースのページを取得する"""
        results = self._database_query(database_id=database_id, filter_param=filter_param)
        pages: list[T] = []
        for page_entity in results:
            page = self.__convert_page_model(
                page_entity=page_entity,
                include_children=include_children or False,
                cls=cls,
            )
            pages.append(page)
        return pages

    def search_pages(
        self,
        cls: Type[T],
        props: Property | list[Property],
        include_children: bool | None = None,
    ) -> list[T]:
        """ページを検索する"""
        filter_builder = Builder.create()
        for prop in props if isinstance(props, list) else [props]:
            filter_builder = filter_builder.add(prop, Cond.EQUALS)
        filter_param = filter_builder.build()
        return self.retrieve_pages(cls, filter_param=filter_param, include_children=include_children)

    def search_page_by_created_at(
        self,
        cls: Type[T],
        start: date | datetime,
        end: date | datetime | None = None,
    ) -> list[T]:
        """指定された日付範囲内のページを取得する"""
        filter_builder = Builder.create()
        filter_builder = filter_builder.add_created_at(Cond.ON_OR_AFTER, start.isoformat())
        if end is not None:
            filter_builder = filter_builder.add_created_at(Cond.ON_OR_BEFORE, end.isoformat())
        return self.retrieve_pages(cls, filter_param=filter_builder.build())

    def search_page_by_last_edited_at(
        self,
        cls: Type[T],
        start: date | datetime,
        end: date | datetime | None = None,
    ) -> list[T]:
        """指定された日付範囲内のページを取得する"""
        filter_builder = Builder.create()
        filter_builder = filter_builder.add_last_edited_at(Cond.ON_OR_AFTER, start.isoformat())
        if end is not None:
            filter_builder = filter_builder.add_last_edited_at(Cond.ON_OR_BEFORE, end.isoformat())
        return self.retrieve_pages(cls, filter_param=filter_builder.build())

    def retrieve_pages(
        self,
        cls: Type[T],
        filter_param: dict | None = None,
        include_children: bool | None = None,
    ) -> list[T]:
        return self.retrieve_database(
            database_id=cls._get_database_id(),
            filter_param=filter_param,
            include_children=include_children,
            cls=cls,
        )

    def find_page(
        self,
        cls: Type[T],
        prop: Title | Text,
        prop_name: str | None = None,
    ) -> T | None:
        """指定されたデータベースのページを取得する。検索可能なプロパティはTitleとTextのみ"""
        filter_param = (
            Builder.create()
            .add(
                prop,
                Cond.EQUALS,
            )
            .build()
        )
        pages = self.retrieve_pages(cls, filter_param=filter_param)
        if len(pages) == 0:
            return None
        if len(pages) > 1:
            warning_message = f"Found multiple pages with the same property: {prop}"
            self._logger.warning(warning_message)
        return pages[0]

    def find_page_by_title(
        self,
        database_id: str,
        title: str,
        title_key_name: str = "名前",
        cls: Type[T] = BasePage,
    ) -> T | None:
        """文字列をもとにデータベースのページを取得する"""
        filter_param = Builder.create()._add(Prop.RICH_TEXT, title_key_name, Cond.EQUALS, title).build()
        results = self.retrieve_database(
            database_id=database_id,
            filter_param=filter_param,
            cls=cls,
        )
        if len(results) == 0:
            return None
        if len(results) > 1:
            warning_message = f"Found multiple pages with the same title: {title}"
            self._logger.warning(warning_message)
        return results[0]

    def find_page_by_unique_id(
        self,
        database_id: str,
        unique_id: int,
        cls: Type[T] = BasePage,
    ) -> T | None:
        """UniqueIdをもとにデータベースのページを取得する"""
        unique_id_prop_name = None
        base_page = self._fetch_sample_page(database_id=database_id, cls=cls)
        for propety in base_page.properties.values:
            if propety.TYPE == "unique_id":
                unique_id_prop_name = propety.name
                break

        if unique_id_prop_name is None:
            raise ValueError("unique_id property is not found")

        filter_param = Builder.create()._add(Prop.ID, unique_id_prop_name, Cond.EQUALS, unique_id).build()
        results = self.retrieve_database(
            database_id=database_id,
            filter_param=filter_param,
            cls=cls,
        )
        if len(results) == 0:
            return None
        return results[0]

    def _convert_to_update_page_object(self, page: T) -> T:
        properties = page.properties.exclude_for_update()
        values = properties.values
        for value in values:
            if isinstance(value, Select) and value._is_set_name_only():
                new_value = self.fetch_select(page.__class__, value.__class__, value.selected_name)
                properties = properties.append_property(new_value)
            if isinstance(value, MultiSelect) and value._is_value_only():
                new_value = self.fetch_multi_select(page.__class__, value.__class__, value.to_str_list())
                properties = properties.append_property(new_value)
        page.properties = properties
        return page

    def _database_query(
        self,
        database_id: str,
        filter_param: dict | None = None,
        start_cursor: str | None = None,
    ) -> dict:
        if filter_param is None:
            return self._database_query_without_filter(database_id=database_id, start_cursor=start_cursor)
        results = []
        while True:
            data = self.__database_query(
                database_id=database_id,
                filter_param=filter_param,
                start_cursor=start_cursor,
            )
            results += data.get("results")
            if not data.get("has_more"):
                return results
            start_cursor = data.get("next_cursor")

    def _database_query_without_filter(self, database_id: str, start_cursor: str | None = None) -> dict:
        results = []
        while True:
            data = self.__database_query(
                database_id=database_id,
                start_cursor=start_cursor,
            )
            results += data.get("results")
            if not data.get("has_more"):
                return results
            start_cursor = data.get("next_cursor")

    def list_blocks(self, block_id: str) -> list[Block]:
        """指定されたブロックの子ブロックを取得する"""
        return self.__get_block_children(page_id=block_id)

    def append_block(self, block_id: str, block: Block) -> None:
        """指定されたブロックに子ブロックを追加する"""
        return self.append_blocks(block_id=block_id, blocks=[block])

    def append_blocks(self, block_id: str, blocks: list[Block]) -> None:
        """指定されたブロックに子ブロックを追加する"""
        return self.__append_block_children(
            block_id=block_id,
            children=[b.to_dict(for_create=True) for b in blocks],
        )

    def append_comment(self, page_id: str, text: str) -> dict:
        """指定されたページにコメントを追加する"""
        return self.client.comments.create(
            parent={"page_id": page_id},
            rich_text=[{"text": {"content": text}}],
        )

    def clear_page(self, page_id: str) -> None:
        """指定されたページのブロックを削除する"""
        blocks = self.list_blocks(block_id=page_id)
        for block in blocks:
            if block.id is None:
                raise ValueError(f"block_id is None: {block}")
            self.client.blocks.delete(block_id=block.id)

    def remove_page(self, page_id: str) -> None:
        """指定されたページを削除する"""
        self.__archive(page_id=page_id)

    def fetch_select(self, cls: Type[T], prop_type: Type[S], value: str) -> S:
        """指定されたデータベースのセレクトを取得する"""
        prop_cache_key = cls.DATABASE_ID + prop_type.__name__
        if prop_cache_key in SELECT_CACHE and SELECT_CACHE[prop_cache_key].has(value):
            return SELECT_CACHE[prop_cache_key].get(value)
        pages = self.retrieve_pages(cls)
        for page in pages:
            prop = page.get_prop(prop_type)
            if prop.selected_name == value:
                cache = SELECT_CACHE[prop_cache_key] if prop_cache_key in SELECT_CACHE else None
                if cache is None:
                    cache = SelectCache[S]()
                cache.set(value, prop)
                SELECT_CACHE[prop_cache_key] = cache
                return prop
        raise ValueError(
            f"Select not found in database. Lotion can get only used selects.: cls={cls.__name__}, prop={prop.__name__}, value={value}"
        )

    def fetch_multi_select(self, cls: Type[T], prop_cls: Type[M], value: str | list[str]) -> M:
        """
        指定されたデータベースのマルチセレクトを取得する。
        ただし現在のデータベースで利用されていないマルチセレクトを取得することはできない。
        """
        value = value if isinstance(value, list) else [value]
        prop_cache_key = cls.DATABASE_ID + prop_cls.__name__
        if prop_cache_key in MULTI_SELECT_CACHE:
            cache = MULTI_SELECT_CACHE[prop_cache_key]
            cached_elements: list[MultiSelectElement] = []
            for v in value:
                if cache.has(v):
                    cached_elements.append(cache.get(v))
            if len(cached_elements) == len(value):
                return prop_cls.from_elements(name=prop_cls.PROP_NAME, elements=cached_elements)
        pages = self.retrieve_pages(cls)
        elements: list[MultiSelectElement] = []
        for page in pages:
            multi_select_elements = page.get_prop(prop_cls).values
            for e in multi_select_elements:
                if e.name in value:
                    elements.append(e)
            elements = list(set(elements))
            if len(elements) == len(value):
                break
        if len(elements) != len(value):
            raise ValueError(
                f"MultiSelect not found in database. Lotion can get only used multi_selects.: cls={cls.__name__}, prop={prop_cls.__name__}, value={value}"
            )
        cache = MULTI_SELECT_CACHE[prop_cache_key] if prop_cache_key in MULTI_SELECT_CACHE else None
        if cache is None:
            cache = MultiSelectCache()
        for e in elements:
            cache.set(e.name, e)
        MULTI_SELECT_CACHE[prop_cache_key] = cache
        return prop_cls.from_elements(name=prop_cls.PROP_NAME, elements=[e for e in elements if e.name in value])

    def __append_block_children(self, block_id: str, children: list[dict], retry_count: int = 0) -> None:
        try:
            _ = self.client.blocks.children.append(block_id=block_id, children=children)
        except APIResponseError as e:
            if self.__is_able_retry(status=e.status, retry_count=retry_count):
                return self.__append_block_children(block_id=block_id, children=children, retry_count=retry_count + 1)
            raise NotionApiError(page_id=block_id, e=e) from e
        except HTTPResponseError as e:
            if self.__is_able_retry(status=e.status, retry_count=retry_count):
                return self.__append_block_children(block_id=block_id, children=children, retry_count=retry_count + 1)
            raise NotionApiError(page_id=block_id, e=e) from e
        except TypeError as e:
            raise AppendBlockError(block_id=block_id, blocks=children, e=e) from e

    def __convert_page_model(
        self,
        page_entity: dict,
        include_children: bool | None = None,
        cls: Type[T] = BasePage,
    ) -> T:
        include_children = (
            include_children if include_children is not None else True
        )  # 未指定の場合はchildrenを取得する
        id_ = PageId(page_entity["id"])
        block_children = self.__get_block_children(page_id=id_.value) if include_children else []
        return cls.from_data(data=page_entity, block_children=block_children)

    def __retrieve_page(self, page_id: str, retry_count: int = 0) -> dict:
        try:
            return self.client.pages.retrieve(page_id=page_id)
        except APIResponseError as e:
            if self.__is_able_retry(status=e.status, retry_count=retry_count):
                return self.__retrieve_page(page_id=page_id, retry_count=retry_count + 1)
            raise NotionApiError(page_id=page_id, e=e) from e
        except HTTPResponseError as e:
            if self.__is_able_retry(status=e.status, retry_count=retry_count):
                return self.__retrieve_page(page_id=page_id, retry_count=retry_count + 1)
            raise NotionApiError(page_id=page_id, e=e) from e

    def __get_block_children(self, page_id: str) -> list[Block]:
        block_entities = self.__list_blocks(block_id=page_id)["results"]
        return [BlockFactory.create(b) for b in block_entities]

    def __list_blocks(self, block_id: str, retry_count: int = 0) -> dict:
        try:
            return self.client.blocks.children.list(block_id=block_id)
        except APIResponseError as e:
            if self.__is_able_retry(status=e.status, retry_count=retry_count):
                return self.__list_blocks(block_id=block_id, retry_count=retry_count + 1)
            raise NotionApiError(page_id=block_id, e=e) from e
        except HTTPResponseError as e:
            if self.__is_able_retry(status=e.status, retry_count=retry_count):
                return self.__list_blocks(block_id=block_id, retry_count=retry_count + 1)
            raise NotionApiError(page_id=block_id, e=e) from e

    def __archive(self, page_id: str, retry_count: int = 0) -> dict:
        try:
            return self.client.pages.update(
                page_id=page_id,
                archived=True,
            )
        except APIResponseError as e:
            if self.__is_able_retry(status=e.status, retry_count=retry_count):
                return self.__archive(page_id=page_id, retry_count=retry_count + 1)
            raise NotionApiError(page_id=page_id, e=e) from e
        except HTTPResponseError as e:
            if self.__is_able_retry(status=e.status, retry_count=retry_count):
                return self.__archive(page_id=page_id, retry_count=retry_count + 1)
            raise NotionApiError(page_id=page_id, e=e) from e

    def __update(self, page_id: str, properties: Properties, retry_count: int = 0) -> None:
        try:
            _ = self.client.pages.update(
                page_id=page_id,
                properties=properties.exclude_for_update().__dict__(),
            )
        except APIResponseError as e:
            if self.__is_able_retry(status=e.status, retry_count=retry_count):
                return self.__update(page_id=page_id, properties=properties, retry_count=retry_count + 1)
            raise NotionApiError(page_id=page_id, e=e, properties=properties) from e
        except HTTPResponseError as e:
            if self.__is_able_retry(status=e.status, retry_count=retry_count):
                return self.__update(page_id=page_id, properties=properties, retry_count=retry_count + 1)
            raise NotionApiError(page_id=page_id, e=e, properties=properties) from e

    def __create_page(
        self,
        database_id: str,
        properties: dict,
        cover: dict | None = None,
        retry_count: int = 0,
    ) -> dict:
        try:
            return self.client.pages.create(
                parent={"type": "database_id", "database_id": database_id},
                cover=cover,
                properties=properties,
            )
        except APIResponseError as e:
            if self.__is_able_retry(status=e.status, retry_count=retry_count):
                self.__create_page(
                    database_id=database_id,
                    properties=properties,
                    cover=cover,
                    retry_count=retry_count + 1,
                )
            raise NotionApiError(database_id=database_id, e=e, properties=properties) from e
        except HTTPResponseError as e:
            if self.__is_able_retry(status=e.status, retry_count=retry_count):
                self.__create_page(
                    database_id=database_id,
                    properties=properties,
                    cover=cover,
                    retry_count=retry_count + 1,
                )
            raise NotionApiError(database_id=database_id, e=e, properties=properties) from e

    def _fetch_sample_page(self, database_id: str, cls: Type[T] = BasePage) -> T:
        """指定されたデータベースのサンプルページを取得する"""
        data = self.__database_query(database_id=database_id, page_size=1)
        pages: list[dict] = data["results"]
        if len(pages) == 0:
            raise ValueError(f"Database has no page. Please create any page. database_id: {database_id}")
        return self.__convert_page_model(page_entity=pages[0], include_children=False, cls=cls)

    def __database_query(
        self,
        database_id: str,
        start_cursor: str | None = None,
        filter_param: dict | None = None,
        page_size: int = 100,
        retry_count: int = 0,
    ) -> dict:
        try:
            if filter_param is None:
                body = {}
                if start_cursor:
                    body["start_cursor"] = start_cursor
                if page_size:
                    body["page_size"] = page_size
                return self.client.request(
                    method="POST",
                    path=f"databases/{database_id}/query",
                    body=body,
                )
            body = {"filter": filter_param}
            if start_cursor:
                body["start_cursor"] = start_cursor
            if page_size:
                body["page_size"] = page_size
            return self.client.request(
                method="POST",
                path=f"databases/{database_id}/query",
                body=body,
            )
        except APIResponseError as e:
            if self.__is_able_retry(status=e.status, retry_count=retry_count):
                return self.__database_query(
                    database_id=database_id,
                    start_cursor=start_cursor,
                    filter_param=filter_param,
                    retry_count=retry_count + 1,
                )
            raise NotionApiError(database_id=database_id, e=e) from e
        except HTTPResponseError as e:
            if self.__is_able_retry(status=e.status, retry_count=retry_count):
                return self.__database_query(
                    database_id=database_id,
                    start_cursor=start_cursor,
                    filter_param=filter_param,
                    retry_count=retry_count + 1,
                )
            raise NotionApiError(database_id=database_id, e=e) from e

    def __is_able_retry(self, status: int, retry_count: int) -> bool:
        return status == NOTION_API_ERROR_BAD_GATEWAY and retry_count < self.max_retry_count
