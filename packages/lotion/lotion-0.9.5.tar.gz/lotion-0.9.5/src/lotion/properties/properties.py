from dataclasses import dataclass

from .property import Property
from .title import Title


@dataclass(frozen=True)
class Properties:
    values: list[Property]

    def __post_init__(self) -> None:
        for value in self.values:
            if not isinstance(value, Property):
                msg = f"values must be Property. value: {value}"
                raise TypeError(msg)

    def __dict__(self) -> dict:
        result = {}
        for value in self.values:
            result = {**result, **value.__dict__()}
        return result

    def append_property(self, prop: Property) -> "Properties":
        props = []

        is_updated = False
        for original_prop in self.values:
            if original_prop is None:
                # この場合があるらしい。どこかで混じったかな?
                continue
            if prop.name == original_prop.name:
                props.append(prop)
                is_updated = True
            else:
                props.append(original_prop)

        # valuesにない場合は新規で追加する
        if not is_updated:
            props.append(prop)

        return Properties(values=props)

    def get_title(self) -> Title:
        for value in self.values:
            if isinstance(value, Title):
                return value
        msg = f"Title property not found. properties: {self.values}"
        raise Exception(msg)

    def get_property(self, name: str, instance_class: type) -> Property | None:
        for value in self.values:
            if isinstance(value, instance_class) and value.name == name:
                return value
        return None

    def exclude_for_update(self) -> "Properties":
        """
        更新時にエラーとなるプロパティを除外する
        """
        exclude_types = [
            "button",
            "created_by",
            "last_edited_by",
            "formula",
            "rollup",
            "unique_id",
            "files",
        ]
        return Properties(values=[prop for prop in self.values if prop.TYPE not in exclude_types])

    def is_empty(self) -> bool:
        return len(self.values) == 0
