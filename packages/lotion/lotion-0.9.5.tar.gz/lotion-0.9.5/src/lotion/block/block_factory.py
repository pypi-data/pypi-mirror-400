from dataclasses import dataclass

from lotion.block.block import Block
from lotion.block.block_type import BlockType
from lotion.block.bookmark import Bookmark
from lotion.block.bulleted_list_item import BulletedListItem
from lotion.block.callout import Callout
from lotion.block.child_database import ChildDatabase
from lotion.block.child_page import ChildPage
from lotion.block.code import Code
from lotion.block.column_list import ColumnList
from lotion.block.divider import Divider
from lotion.block.embed import Embed
from lotion.block.heading import Heading
from lotion.block.image import Image
from lotion.block.numbered_list_item import NumberedListItem
from lotion.block.paragraph import Paragraph
from lotion.block.quote import Quote
from lotion.block.table import Table
from lotion.block.to_do import ToDo
from lotion.block.video import Video


@dataclass
class BlockFactory:
    @staticmethod
    def create(block: dict) -> Block:
        # import json

        # print(json.dumps(block, indent=2, ensure_ascii=False))
        if block["object"] != "block":
            raise ValueError("block must be of type block")
        block_type = BlockType(block["type"])
        match block_type:
            case BlockType.VIDEO:
                return Video.of(block)
            case BlockType.PARAGRAPH:
                return Paragraph.of(block)
            case BlockType.QUOTE:
                return Quote.of(block)
            case BlockType.HEADING_1:
                return Heading.of(block)
            case BlockType.HEADING_2:
                return Heading.of(block)
            case BlockType.HEADING_3:
                return Heading.of(block)
            case BlockType.DIVIDER:
                return Divider.of(block)
            case BlockType.BULLETED_LIST_ITEM:
                return BulletedListItem.of(block)
            case BlockType.EMBED:
                return Embed.of(block)
            case BlockType.BOOKMARK:
                return Bookmark.of(block)
            case BlockType.IMAGE:
                return Image.of(block)
            case BlockType.CODE:
                return Code.of(block)
            case BlockType.TABLE:
                return Table.of(block)
            case BlockType.NUMBERED_LIST_ITEM:
                return NumberedListItem.of(block)
            case BlockType.CHILD_DATABASE:
                return ChildDatabase.of(block)
            case BlockType.TO_DO:
                return ToDo.of(block)
            case BlockType.CALLOUT:
                return Callout.of(block)
            case BlockType.CHILD_PAGE:
                return ChildPage.of(block)
            case BlockType.COLUMN_LIST:
                return ColumnList.of(block)
            case _:
                import json

                block_json = json.dumps(block, ensure_ascii=False)
                msg = f"block type is not supported {block_type}\n{block_json}"
                raise ValueError(msg)
