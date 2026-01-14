from enum import IntEnum
from typing import Literal

__all__ = ["MatchType", "SortOrder"]


class MatchType(IntEnum):
    """Match type enumeration."""

    CASUAL = 1
    RANKED = 2
    PRIVATE = 3
    EVENT = 4


SortOrder = Literal["newest", "oldest", "fastest", "slowest"]
