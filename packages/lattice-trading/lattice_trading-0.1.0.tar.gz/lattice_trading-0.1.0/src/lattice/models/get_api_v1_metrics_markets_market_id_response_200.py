
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1MetricsMarketsMarketIdResponse200")


@_attrs_define
class GetApiV1MetricsMarketsMarketIdResponse200:
    """
    Attributes:
        market_id (str):
        volume_cents (float):
        open_interest (float):
    """

    market_id: str
    volume_cents: float
    open_interest: float

    def to_dict(self) -> dict[str, Any]:
        market_id = self.market_id

        volume_cents = self.volume_cents

        open_interest = self.open_interest

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "marketId": market_id,
                "volumeCents": volume_cents,
                "openInterest": open_interest,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        market_id = d.pop("marketId")

        volume_cents = d.pop("volumeCents")

        open_interest = d.pop("openInterest")

        get_api_v1_metrics_markets_market_id_response_200 = cls(
            market_id=market_id,
            volume_cents=volume_cents,
            open_interest=open_interest,
        )

        return get_api_v1_metrics_markets_market_id_response_200
