
from __future__ import annotations

from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostApiV1OrdersResponse201")


@_attrs_define
class PostApiV1OrdersResponse201:
    """
    Attributes:
        id (str):
        market_id (str):
        outcome_id (str):
        side (str):
        type (str):
        price (Union[None, float]):
        quantity (float):
        status (str):
        created_at (str):
    """

    id: str
    market_id: str
    outcome_id: str
    side: str
    type: str
    price: None | float
    quantity: float
    status: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        market_id = self.market_id

        outcome_id = self.outcome_id

        side = self.side

        type = self.type

        price: None | float
        price = self.price

        quantity = self.quantity

        status = self.status

        created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "marketId": market_id,
                "outcomeId": outcome_id,
                "side": side,
                "type": type,
                "price": price,
                "quantity": quantity,
                "status": status,
                "createdAt": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        market_id = d.pop("marketId")

        outcome_id = d.pop("outcomeId")

        side = d.pop("side")

        type = d.pop("type")

        def _parse_price(data: object) -> None | float:
            if data is None:
                return data
            return cast(None | float, data)

        price = _parse_price(d.pop("price"))

        quantity = d.pop("quantity")

        status = d.pop("status")

        created_at = d.pop("createdAt")

        post_api_v1_orders_response_201 = cls(
            id=id,
            market_id=market_id,
            outcome_id=outcome_id,
            side=side,
            type=type,
            price=price,
            quantity=quantity,
            status=status,
            created_at=created_at,
        )

        return post_api_v1_orders_response_201
