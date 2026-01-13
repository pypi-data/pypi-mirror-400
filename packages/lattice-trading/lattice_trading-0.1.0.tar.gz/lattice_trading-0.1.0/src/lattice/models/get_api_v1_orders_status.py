
from __future__ import annotations

from enum import Enum


class GetApiV1OrdersStatus(str, Enum):
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    FILLED = "filled"
    OPEN = "open"
    PARTIALLY_FILLED = "partially_filled"
    PENDING = "pending"
    REJECTED = "rejected"

    def __str__(self) -> str:
        return str(self.value)
