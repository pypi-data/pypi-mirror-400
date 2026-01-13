
from __future__ import annotations

from enum import Enum


class GetApiV1MetricsTimeseriesResponse200Interval(str, Enum):
    DAY = "day"
    WEEK = "week"

    def __str__(self) -> str:
        return str(self.value)
