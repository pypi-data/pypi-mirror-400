
from __future__ import annotations

from enum import Enum


class PatchApiV1MarketsMarketIdBodyType(str, Enum):
    BINARY = "binary"
    CATEGORICAL = "categorical"
    SCALAR = "scalar"

    def __str__(self) -> str:
        return str(self.value)
