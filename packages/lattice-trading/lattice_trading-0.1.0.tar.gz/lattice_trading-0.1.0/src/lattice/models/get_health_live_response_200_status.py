
from __future__ import annotations

from enum import Enum


class GetHealthLiveResponse200Status(str, Enum):
    OK = "ok"

    def __str__(self) -> str:
        return str(self.value)
