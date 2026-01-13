from dataclasses import dataclass
from typing import Any, Type, TypeVar

from ..properties.prop import Prop
from ..properties.property import Property
from .condition.cond import Cond
from .condition_ruleset import ConditionRuleset

P = TypeVar("P", bound=Property)


@dataclass(frozen=True)
class Builder:
    conditions: list[dict]

    @staticmethod
    def create() -> "Builder":
        return Builder(conditions=[])

    def add(self, prop: Property | Type[Property], cond: Cond) -> "Builder":
        if isinstance(prop, Type):
            return self._add(prop.TYPE, prop.PROP_NAME, cond)
        return self._add(prop.TYPE, prop.name, cond, prop._value_for_filter)

    def add_filter_param(self, param: dict) -> "Builder":
        return Builder(conditions=[*self.conditions, param])

    def add_created_at(self, cond_type: Cond, value: Any) -> "Builder":
        return self._add_timestamp(Prop.CREATED_TIME, cond_type, value)

    def add_last_edited_at(self, cond_type: Cond, value: Any) -> "Builder":
        return self._add_timestamp(Prop.LAST_EDITED_TIME, cond_type, value)

    def _add(self, prop_type: str, prop_name: str, cond_type: Cond, value: Any = None) -> "Builder":
        _prop_type = Prop.from_str(prop_type)
        if _prop_type == Prop.CREATED_TIME:
            raise ValueError(f"You use add_created_at() method for {prop_type}")
        if _prop_type == Prop.LAST_EDITED_TIME:
            raise ValueError(f"You use add_last_edited_at() method for {prop_type}")

        param = ConditionRuleset(_prop_type, prop_name, cond_type, value).validate().generate_param()
        return Builder(conditions=[*self.conditions, param])

    def _add_timestamp(self, prop_type: Prop, cond_type: Cond, value: Any) -> "Builder":
        param = ConditionRuleset(prop_type, "", cond_type, value).validate().generate_param()
        return Builder(conditions=[*self.conditions, param])

    def is_empty(self) -> bool:
        return len(self.conditions) == 0

    def build(self, mode: str = "and") -> dict:
        """
        :param mode: "and" or "or"

        """
        if len(self.conditions) == 0:
            raise ValueError("Filter is empty")
        if len(self.conditions) == 1:
            return self.conditions[0]
        return {
            mode: self.conditions,
        }
