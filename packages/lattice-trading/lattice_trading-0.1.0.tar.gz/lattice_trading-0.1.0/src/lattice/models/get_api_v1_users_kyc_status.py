
from __future__ import annotations

from enum import Enum


class GetApiV1UsersKycStatus(str, Enum):
    APPROVED = "approved"
    NONE = "none"
    PENDING = "pending"
    REJECTED = "rejected"

    def __str__(self) -> str:
        return str(self.value)
