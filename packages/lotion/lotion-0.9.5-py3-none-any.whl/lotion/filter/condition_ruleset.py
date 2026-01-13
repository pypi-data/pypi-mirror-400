import re
from dataclasses import dataclass
from typing import Any

from ..page.page_id import PageId
from ..properties.prop import Prop
from .condition.cond import Cond


class TrueValue:
    pass


class EmptyObject:
    pass


RULESET: dict[Prop, dict[Cond, list[type]]] = {}
RULESET[Prop.RICH_TEXT] = {
    Cond.EQUALS: [str],
    Cond.DOES_NOT_EQUAL: [str],
    Cond.CONTAINS: [str],
    Cond.DOES_NOT_CONTAIN: [str],
    Cond.IS_EMPTY: [TrueValue],
    Cond.IS_NOT_EMPTY: [TrueValue],
    Cond.STARTS_WITH: [str],
    Cond.ENDS_WITH: [str],
}
RULESET[Prop.CHECKBOX] = {
    Cond.EQUALS: [bool],
    Cond.DOES_NOT_EQUAL: [bool],
}
RULESET[Prop.DATE] = {
    Cond.EQUALS: [str],
    Cond.AFTER: [str],
    Cond.ON_OR_AFTER: [str],
    Cond.BEFORE: [str],
    Cond.ON_OR_BEFORE: [str],
    Cond.IS_EMPTY: [TrueValue],
    Cond.IS_NOT_EMPTY: [TrueValue],
    Cond.NEXT_WEEK: [EmptyObject],
    Cond.NEXT_MONTH: [EmptyObject],
    Cond.NEXT_YEAR: [EmptyObject],
    Cond.PAST_WEEK: [EmptyObject],
    Cond.PAST_MONTH: [EmptyObject],
    Cond.PAST_YEAR: [EmptyObject],
    Cond.THIS_WEEK: [EmptyObject],
}
RULESET[Prop.FILES] = {
    Cond.IS_EMPTY: [TrueValue],
    Cond.IS_NOT_EMPTY: [TrueValue],
}
RULESET[Prop.MULTI_SELECT] = {
    Cond.CONTAINS: [str],
    Cond.DOES_NOT_CONTAIN: [str],
    Cond.IS_EMPTY: [TrueValue],
    Cond.IS_NOT_EMPTY: [TrueValue],
}
RULESET[Prop.NUMBER] = {
    Cond.EQUALS: [int, float],
    Cond.DOES_NOT_EQUAL: [int, float],
    Cond.GREATER_THAN: [int, float],
    Cond.LESS_THAN: [int, float],
    Cond.GREATER_THAN_OR_EQUAL_TO: [int, float],
    Cond.LESS_THAN_OR_EQUAL_TO: [int, float],
    Cond.IS_EMPTY: [TrueValue],
    Cond.IS_NOT_EMPTY: [TrueValue],
}
RULESET[Prop.PEOPLE] = {
    Cond.CONTAINS: [str],
    Cond.DOES_NOT_CONTAIN: [str],
    Cond.IS_EMPTY: [TrueValue],
    Cond.IS_NOT_EMPTY: [TrueValue],
}
RULESET[Prop.RELATION] = {
    Cond.CONTAINS: [str],
    Cond.DOES_NOT_CONTAIN: [str],
    Cond.IS_EMPTY: [TrueValue],
    Cond.IS_NOT_EMPTY: [TrueValue],
}
RULESET[Prop.SELECT] = {
    Cond.EQUALS: [str],
    Cond.DOES_NOT_EQUAL: [str],
    Cond.IS_EMPTY: [TrueValue],
    Cond.IS_NOT_EMPTY: [TrueValue],
}
RULESET[Prop.STATUS] = {
    Cond.EQUALS: [str],
    Cond.DOES_NOT_EQUAL: [str],
    Cond.IS_EMPTY: [TrueValue],
    Cond.IS_NOT_EMPTY: [TrueValue],
}
RULESET[Prop.ID] = {
    Cond.EQUALS: [int],
    Cond.DOES_NOT_EQUAL: [int],
    Cond.GREATER_THAN: [int],
    Cond.LESS_THAN: [int],
    Cond.GREATER_THAN_OR_EQUAL_TO: [int],
    Cond.LESS_THAN_OR_EQUAL_TO: [int],
    Cond.IS_EMPTY: [TrueValue],
    Cond.IS_NOT_EMPTY: [TrueValue],
}
RULESET[Prop.CREATED_TIME] = {
    Cond.EQUALS: [str],
    Cond.AFTER: [str],
    Cond.ON_OR_AFTER: [str],
    Cond.BEFORE: [str],
    Cond.ON_OR_BEFORE: [str],
    Cond.IS_EMPTY: [TrueValue],
    Cond.IS_NOT_EMPTY: [TrueValue],
    Cond.NEXT_WEEK: [EmptyObject],
    Cond.NEXT_MONTH: [EmptyObject],
    Cond.NEXT_YEAR: [EmptyObject],
    Cond.PAST_WEEK: [EmptyObject],
    Cond.PAST_MONTH: [EmptyObject],
    Cond.PAST_YEAR: [EmptyObject],
    Cond.THIS_WEEK: [EmptyObject],
}
RULESET[Prop.LAST_EDITED_TIME] = {
    Cond.EQUALS: [str],
    Cond.AFTER: [str],
    Cond.ON_OR_AFTER: [str],
    Cond.BEFORE: [str],
    Cond.ON_OR_BEFORE: [str],
    Cond.IS_EMPTY: [TrueValue],
    Cond.IS_NOT_EMPTY: [TrueValue],
    Cond.NEXT_WEEK: [EmptyObject],
    Cond.NEXT_MONTH: [EmptyObject],
    Cond.NEXT_YEAR: [EmptyObject],
    Cond.PAST_WEEK: [EmptyObject],
    Cond.PAST_MONTH: [EmptyObject],
    Cond.PAST_YEAR: [EmptyObject],
    Cond.THIS_WEEK: [EmptyObject],
}


@dataclass(frozen=True)
class ConditionRuleset:
    prop: Prop
    prop_name: str
    cond: Cond
    value: Any

    def validate(self) -> "ConditionRuleset":
        # 必須のチェック
        self.validate_prop()
        self.validate_cond()
        self.validate_value()

        # オプションのチェック
        self.validate_page_id()
        self.validate_date()

        return self

    def generate_param(self) -> Any:
        if self.prop == Prop.CREATED_TIME or self.prop == Prop.LAST_EDITED_TIME:
            return self._generate_timestamp_param()
        value = self._get_value()
        return {
            "property": self.prop_name,
            self.prop.value: {
                self.cond.value: value,
            },
        }

    def _generate_timestamp_param(self) -> Any:
        value = self._get_value()
        return {
            "timestamp": self.prop.value,
            self.prop.value: {
                self.cond.value: value,
            },
        }

    def _get_value(self) -> Any:
        conds = RULESET[self.prop][self.cond]
        if TrueValue in conds:
            return True
        if EmptyObject in conds:
            return {}
        return self.value

    def validate_prop(self) -> None:
        if self.prop not in RULESET:
            raise ValueError(f"Property {self.prop} is not supported")

    def validate_cond(self) -> None:
        if self.cond not in RULESET[self.prop]:
            msg = f"Condition {self.cond} is not supported for property {self.prop}"
            raise ValueError(msg)

    def validate_value(self) -> None:
        conds = RULESET[self.prop][self.cond]
        if TrueValue in conds:
            return
        if EmptyObject in conds:
            return
        # strやint、floatなどの型が含まれているかどうかを確認する
        if type(self.value) not in conds:
            msg = f"Value type {type(self.value)} is not supported for property {self.prop} with condition {self.cond}"
            raise ValueError(msg)

    def validate_page_id(self) -> None:
        if self.prop not in [Prop.PEOPLE, Prop.RELATION]:
            return
        if self.cond not in [Cond.CONTAINS, Cond.DOES_NOT_CONTAIN]:
            return
        # ユーザもしくはリレーションの場合は、ページIDに変換できるかどうかを確認する
        PageId(self.value)

    def validate_date(self) -> None:
        if self.prop != Prop.DATE:
            return
        if self.cond not in [
            Cond.AFTER,
            Cond.ON_OR_AFTER,
            Cond.BEFORE,
            Cond.ON_OR_BEFORE,
        ]:
            return
        # "2021-05-10"、"2021-05-10T12:00:00"、"2021-10-15T12:00:00-07:00"
        # のような形式であるかどうかを正規表現で確認する
        if re.match(r"\d{4}-\d{2}-\d{2}", self.value):
            return
        if re.match(r"\d{4}-\d{2}-\d{2}T?\d{2}:\d{2}:\d{2}", self.value):
            return
        if re.match(r"\d{4}-\d{2}-\d{2}T?\d{2}:\d{2}:\d{2}[-+]?\d{2}:\d{2}", self.value):
            return
        raise ValueError(f"Date value {self.value} is invalid")
