
from __future__ import annotations

from enum import Enum


class GetApiV1MarketsStatus(str, Enum):
    CLOSED = "closed"
    DRAFT = "draft"
    OPEN = "open"
    RESOLVED = "resolved"
    SUSPENDED = "suspended"
    VOIDED = "voided"

    def __str__(self) -> str:
        return str(self.value)
