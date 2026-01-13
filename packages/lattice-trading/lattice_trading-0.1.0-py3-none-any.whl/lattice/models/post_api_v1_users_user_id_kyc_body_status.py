
from __future__ import annotations

from enum import Enum


class PostApiV1UsersUserIdKycBodyStatus(str, Enum):
    APPROVED = "approved"
    PENDING = "pending"
    REJECTED = "rejected"

    def __str__(self) -> str:
        return str(self.value)
