
from __future__ import annotations

from enum import Enum


class PostApiV1ApiKeysBodyScopesItem(str, Enum):
    ADMINCOMPLIANCE = "admin:compliance"
    ADMINMARKETS = "admin:markets"
    ADMINUSERS = "admin:users"
    READACCOUNT = "read:account"
    READMARKETS = "read:markets"
    READORDERS = "read:orders"
    READPOSITIONS = "read:positions"
    READTRADES = "read:trades"
    WRITEACCOUNT = "write:account"
    WRITEMARKETS = "write:markets"
    WRITEORDERS = "write:orders"

    def __str__(self) -> str:
        return str(self.value)
