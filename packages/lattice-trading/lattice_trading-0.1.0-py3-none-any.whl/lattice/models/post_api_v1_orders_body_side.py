
from __future__ import annotations

from enum import Enum


class PostApiV1OrdersBodySide(str, Enum):
    BUY = "buy"
    SELL = "sell"

    def __str__(self) -> str:
        return str(self.value)
