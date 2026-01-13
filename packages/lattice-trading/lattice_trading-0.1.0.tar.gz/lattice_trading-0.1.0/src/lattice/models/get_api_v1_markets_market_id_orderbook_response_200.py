
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_markets_market_id_orderbook_response_200_asks_item import (
        GetApiV1MarketsMarketIdOrderbookResponse200AsksItem,
    )
    from ..models.get_api_v1_markets_market_id_orderbook_response_200_bids_item import (
        GetApiV1MarketsMarketIdOrderbookResponse200BidsItem,
    )


T = TypeVar("T", bound="GetApiV1MarketsMarketIdOrderbookResponse200")


@_attrs_define
class GetApiV1MarketsMarketIdOrderbookResponse200:
    """
    Attributes:
        market_id (str):
        outcome_id (str):
        bids (List['GetApiV1MarketsMarketIdOrderbookResponse200BidsItem']):
        asks (List['GetApiV1MarketsMarketIdOrderbookResponse200AsksItem']):
        updated_at (str):
    """

    market_id: str
    outcome_id: str
    bids: list["GetApiV1MarketsMarketIdOrderbookResponse200BidsItem"]
    asks: list["GetApiV1MarketsMarketIdOrderbookResponse200AsksItem"]
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        market_id = self.market_id

        outcome_id = self.outcome_id

        bids = []
        for bids_item_data in self.bids:
            bids_item = bids_item_data.to_dict()
            bids.append(bids_item)

        asks = []
        for asks_item_data in self.asks:
            asks_item = asks_item_data.to_dict()
            asks.append(asks_item)

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "marketId": market_id,
                "outcomeId": outcome_id,
                "bids": bids,
                "asks": asks,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_markets_market_id_orderbook_response_200_asks_item import (
            GetApiV1MarketsMarketIdOrderbookResponse200AsksItem,
        )
        from ..models.get_api_v1_markets_market_id_orderbook_response_200_bids_item import (
            GetApiV1MarketsMarketIdOrderbookResponse200BidsItem,
        )

        d = src_dict.copy()
        market_id = d.pop("marketId")

        outcome_id = d.pop("outcomeId")

        bids = []
        _bids = d.pop("bids")
        for bids_item_data in _bids:
            bids_item = GetApiV1MarketsMarketIdOrderbookResponse200BidsItem.from_dict(bids_item_data)

            bids.append(bids_item)

        asks = []
        _asks = d.pop("asks")
        for asks_item_data in _asks:
            asks_item = GetApiV1MarketsMarketIdOrderbookResponse200AsksItem.from_dict(asks_item_data)

            asks.append(asks_item)

        updated_at = d.pop("updatedAt")

        get_api_v1_markets_market_id_orderbook_response_200 = cls(
            market_id=market_id,
            outcome_id=outcome_id,
            bids=bids,
            asks=asks,
            updated_at=updated_at,
        )

        return get_api_v1_markets_market_id_orderbook_response_200
