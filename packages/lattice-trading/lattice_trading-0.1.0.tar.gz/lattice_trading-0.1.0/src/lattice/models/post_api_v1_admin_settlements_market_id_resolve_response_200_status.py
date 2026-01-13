
from __future__ import annotations

from enum import Enum


class PostApiV1AdminSettlementsMarketIdResolveResponse200Status(str, Enum):
    RESOLVED = "resolved"

    def __str__(self) -> str:
        return str(self.value)
