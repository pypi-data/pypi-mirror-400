
from __future__ import annotations

from enum import Enum


class GetApiV1MetricsTimeseriesResponse200Metric(str, Enum):
    ACTIVE_MARKETS = "active_markets"
    FEES = "fees"
    REGISTRATIONS = "registrations"
    VOLUME = "volume"

    def __str__(self) -> str:
        return str(self.value)
