
from __future__ import annotations

from enum import Enum


class GetHealthResponse200Status(str, Enum):
    OK = "ok"

    def __str__(self) -> str:
        return str(self.value)
