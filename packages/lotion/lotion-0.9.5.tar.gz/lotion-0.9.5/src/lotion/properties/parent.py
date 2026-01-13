from dataclasses import dataclass


@dataclass
class Parent:
    type: str
    workspace: bool | None = None
