
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1MarketsMarketIdTradesResponse200TradesItem")


@_attrs_define
class GetApiV1MarketsMarketIdTradesResponse200TradesItem:
    """
    Attributes:
        id (str):
        outcome_id (str):
        taker_side (str):
        price (float):
        quantity (float):
        created_at (str):
    """

    id: str
    outcome_id: str
    taker_side: str
    price: float
    quantity: float
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        outcome_id = self.outcome_id

        taker_side = self.taker_side

        price = self.price

        quantity = self.quantity

        created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "outcomeId": outcome_id,
                "takerSide": taker_side,
                "price": price,
                "quantity": quantity,
                "createdAt": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        outcome_id = d.pop("outcomeId")

        taker_side = d.pop("takerSide")

        price = d.pop("price")

        quantity = d.pop("quantity")

        created_at = d.pop("createdAt")

        get_api_v1_markets_market_id_trades_response_200_trades_item = cls(
            id=id,
            outcome_id=outcome_id,
            taker_side=taker_side,
            price=price,
            quantity=quantity,
            created_at=created_at,
        )

        return get_api_v1_markets_market_id_trades_response_200_trades_item
