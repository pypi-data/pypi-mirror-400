
from __future__ import annotations

from enum import Enum


class GetApiV1OrdersSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

    def __str__(self) -> str:
        return str(self.value)
