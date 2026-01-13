
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_markets_market_id_trades_response_200_trades_item import (
        GetApiV1MarketsMarketIdTradesResponse200TradesItem,
    )


T = TypeVar("T", bound="GetApiV1MarketsMarketIdTradesResponse200")


@_attrs_define
class GetApiV1MarketsMarketIdTradesResponse200:
    """
    Attributes:
        market_id (str):
        trades (List['GetApiV1MarketsMarketIdTradesResponse200TradesItem']):
        total (float):
        limit (float):
    """

    market_id: str
    trades: list["GetApiV1MarketsMarketIdTradesResponse200TradesItem"]
    total: float
    limit: float

    def to_dict(self) -> dict[str, Any]:
        market_id = self.market_id

        trades = []
        for trades_item_data in self.trades:
            trades_item = trades_item_data.to_dict()
            trades.append(trades_item)

        total = self.total

        limit = self.limit

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "marketId": market_id,
                "trades": trades,
                "total": total,
                "limit": limit,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_markets_market_id_trades_response_200_trades_item import (
            GetApiV1MarketsMarketIdTradesResponse200TradesItem,
        )

        d = src_dict.copy()
        market_id = d.pop("marketId")

        trades = []
        _trades = d.pop("trades")
        for trades_item_data in _trades:
            trades_item = GetApiV1MarketsMarketIdTradesResponse200TradesItem.from_dict(trades_item_data)

            trades.append(trades_item)

        total = d.pop("total")

        limit = d.pop("limit")

        get_api_v1_markets_market_id_trades_response_200 = cls(
            market_id=market_id,
            trades=trades,
            total=total,
            limit=limit,
        )

        return get_api_v1_markets_market_id_trades_response_200
