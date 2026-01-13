
from __future__ import annotations

from enum import Enum


class GetApiV1AdminAuditExportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"

    def __str__(self) -> str:
        return str(self.value)
