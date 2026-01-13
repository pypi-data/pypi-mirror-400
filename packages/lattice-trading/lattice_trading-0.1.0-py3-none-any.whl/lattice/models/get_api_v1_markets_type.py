
from __future__ import annotations

from enum import Enum


class GetApiV1MarketsType(str, Enum):
    BINARY = "binary"
    CATEGORICAL = "categorical"
    SCALAR = "scalar"

    def __str__(self) -> str:
        return str(self.value)
