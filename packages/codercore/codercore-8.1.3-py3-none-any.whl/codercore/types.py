from enum import StrEnum
from typing import TypeVar

T = TypeVar("T")
SequentialCollection = list[T] | tuple[T, ...]


class UpperStrEnum(StrEnum):
    @staticmethod
    def _generate_next_value_(name: str, *args, **kwargs) -> str:
        return name.upper()
