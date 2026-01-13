
from __future__ import annotations

from enum import Enum


class GetHealthReadyResponse200ChecksAdditionalPropertyStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"

    def __str__(self) -> str:
        return str(self.value)
