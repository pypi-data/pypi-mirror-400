
from __future__ import annotations

from enum import Enum


class PostApiV1UsersUserIdStatusBodyStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    SUSPENDED = "suspended"

    def __str__(self) -> str:
        return str(self.value)
