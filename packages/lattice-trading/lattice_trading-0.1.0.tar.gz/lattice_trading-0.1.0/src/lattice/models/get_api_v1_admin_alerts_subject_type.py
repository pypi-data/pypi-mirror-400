
from __future__ import annotations

from enum import Enum


class GetApiV1AdminAlertsSubjectType(str, Enum):
    ACCOUNT = "account"
    MARKET = "market"
    ORDER = "order"
    TRADE = "trade"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
