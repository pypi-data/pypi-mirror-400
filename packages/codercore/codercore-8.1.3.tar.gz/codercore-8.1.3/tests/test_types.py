from enum import auto

from codercore.types import UpperStrEnum


def test_upper_str_enum_auto():
    class Test(UpperStrEnum):
        EXAMPLE = auto()

    assert Test.EXAMPLE == "EXAMPLE"
