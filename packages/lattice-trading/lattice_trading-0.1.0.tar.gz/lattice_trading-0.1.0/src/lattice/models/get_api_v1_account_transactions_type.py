
from __future__ import annotations

from enum import Enum


class GetApiV1AccountTransactionsType(str, Enum):
    ADJUSTMENT = "adjustment"
    DEPOSIT = "deposit"
    FEE = "fee"
    SETTLEMENT = "settlement"
    SETTLEMENT_PAYOUT = "settlement_payout"
    SETTLEMENT_REFUND = "settlement_refund"
    TRADE_BUY = "trade_buy"
    TRADE_SELL = "trade_sell"
    WITHDRAWAL = "withdrawal"

    def __str__(self) -> str:
        return str(self.value)
