
from __future__ import annotations

from enum import Enum


class GetApiV1AdminAlertsStatus(str, Enum):
    DISMISSED = "dismissed"
    INVESTIGATING = "investigating"
    OPEN = "open"
    RESOLVED = "resolved"

    def __str__(self) -> str:
        return str(self.value)
