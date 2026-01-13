from dataclasses import dataclass


@dataclass
class Icon:
    type: str
    emoji: str | None = None

    @staticmethod
    def of(param: dict) -> "Icon":
        return Icon(
            type=param["type"],
            emoji=param["emoji"] if "emoji" in param else None,
        )
