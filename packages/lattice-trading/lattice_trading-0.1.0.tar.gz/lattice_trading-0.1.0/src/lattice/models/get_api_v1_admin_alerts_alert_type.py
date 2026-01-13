
from __future__ import annotations

from enum import Enum


class GetApiV1AdminAlertsAlertType(str, Enum):
    AML_CONCERN = "aml_concern"
    CONCENTRATION_LIMIT = "concentration_limit"
    KYC_CONCERN = "kyc_concern"
    LAYERING = "layering"
    MARKET_ABUSE = "market_abuse"
    POSITION_LIMIT_BREACH = "position_limit_breach"
    PRICE_MANIPULATION = "price_manipulation"
    RELATED_PARTY_TRADE = "related_party_trade"
    SELF_TRADE = "self_trade"
    SPOOFING = "spoofing"
    VOLUME_ANOMALY = "volume_anomaly"
    WASH_TRADING = "wash_trading"

    def __str__(self) -> str:
        return str(self.value)
