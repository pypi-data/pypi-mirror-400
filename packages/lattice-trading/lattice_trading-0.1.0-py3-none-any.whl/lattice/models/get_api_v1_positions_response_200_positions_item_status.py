
from __future__ import annotations

from enum import Enum


class GetApiV1PositionsResponse200PositionsItemStatus(str, Enum):
    CLOSED = "closed"
    OPEN = "open"

    def __str__(self) -> str:
        return str(self.value)
