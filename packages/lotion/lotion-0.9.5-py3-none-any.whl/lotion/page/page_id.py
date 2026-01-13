import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PageId:
    _value: str

    def __post_init__(self) -> None:
        # 型チェック
        if not isinstance(self._value, str):
            msg = f"page_idは文字列である必要があります: {self._value}"
            raise TypeError(msg)

        # UUID4の形式であることを確認する
        if not re.match(
            r"[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}",
            self._value,
        ):
            msg = f"page_idの形式が不正です: {self._value}"
            raise ValueError(msg)

    @staticmethod
    def dummy() -> "PageId":
        return PageId(_value="5c38fd30-714b-4ce2-bf2d-25407f3cfc16")

    @property
    def value(self) -> str:
        """UUID4の形式の文字列を返す"""
        # まずハイフンを削除してから、ハイフンをつけなおす
        _value = self._value.replace("-", "")
        return "-".join([_value[:8], _value[8:12], _value[12:16], _value[16:20], _value[20:]])
