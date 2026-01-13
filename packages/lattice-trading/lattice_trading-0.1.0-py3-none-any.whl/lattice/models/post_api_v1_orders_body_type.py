
from __future__ import annotations

from enum import Enum


class PostApiV1OrdersBodyType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"

    def __str__(self) -> str:
        return str(self.value)
