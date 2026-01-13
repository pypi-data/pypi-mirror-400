
from __future__ import annotations

from enum import Enum


class GetApiV1MarketsSort(str, Enum):
    CLOSING = "closing"
    NEWEST = "newest"
    TRENDING = "trending"
    VOLUME = "volume"

    def __str__(self) -> str:
        return str(self.value)
