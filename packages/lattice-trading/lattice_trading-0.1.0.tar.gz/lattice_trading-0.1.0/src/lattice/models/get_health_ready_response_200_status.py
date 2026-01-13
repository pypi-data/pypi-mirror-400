
from __future__ import annotations

from enum import Enum


class GetHealthReadyResponse200Status(str, Enum):
    DEGRADED = "degraded"
    HEALTHY = "healthy"
    SHUTTING_DOWN = "shutting_down"
    UNHEALTHY = "unhealthy"

    def __str__(self) -> str:
        return str(self.value)
