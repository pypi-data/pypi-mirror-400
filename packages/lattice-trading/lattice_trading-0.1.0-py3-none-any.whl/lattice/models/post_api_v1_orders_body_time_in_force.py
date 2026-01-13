
from __future__ import annotations

from enum import Enum


class PostApiV1OrdersBodyTimeInForce(str, Enum):
    DAY = "day"
    FOK = "fok"
    GTC = "gtc"
    IOC = "ioc"

    def __str__(self) -> str:
        return str(self.value)
