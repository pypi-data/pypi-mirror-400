from dataclasses import dataclass


@dataclass
class BaseOperator:
    id: str
    object: str

    @staticmethod
    def of(param: dict[str, str]) -> "BaseOperator":
        return BaseOperator(id=param["id"], object=param["object"])
