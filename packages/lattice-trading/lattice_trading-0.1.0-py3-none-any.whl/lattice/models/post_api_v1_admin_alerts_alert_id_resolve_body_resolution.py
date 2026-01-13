
from __future__ import annotations

from enum import Enum


class PostApiV1AdminAlertsAlertIdResolveBodyResolution(str, Enum):
    DISMISSED = "dismissed"
    RESOLVED = "resolved"

    def __str__(self) -> str:
        return str(self.value)
