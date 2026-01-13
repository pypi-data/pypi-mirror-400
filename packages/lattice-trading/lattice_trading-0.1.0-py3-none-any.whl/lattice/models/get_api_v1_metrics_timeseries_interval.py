
from __future__ import annotations

from enum import Enum


class GetApiV1MetricsTimeseriesInterval(str, Enum):
    DAY = "day"
    WEEK = "week"

    def __str__(self) -> str:
        return str(self.value)
