
from __future__ import annotations

from enum import Enum


class PostApiV1AdminSettlementsMarketIdVoidResponse200Status(str, Enum):
    VOIDED = "voided"

    def __str__(self) -> str:
        return str(self.value)
