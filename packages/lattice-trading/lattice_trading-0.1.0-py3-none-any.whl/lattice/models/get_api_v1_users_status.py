
from __future__ import annotations

from enum import Enum


class GetApiV1UsersStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    PENDING_KYC = "pending_kyc"
    SUSPENDED = "suspended"

    def __str__(self) -> str:
        return str(self.value)
