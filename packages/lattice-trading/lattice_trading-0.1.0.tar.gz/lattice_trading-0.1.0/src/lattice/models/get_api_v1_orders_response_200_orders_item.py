
from __future__ import annotations

from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1OrdersResponse200OrdersItem")


@_attrs_define
class GetApiV1OrdersResponse200OrdersItem:
    """
    Attributes:
        id (str):
        market_id (str):
        outcome_id (str):
        user_id (str):
        side (str):
        type (str):
        price (Union[None, float]):
        quantity (float):
        filled_quantity (float):
        status (str):
        created_at (str):
    """

    id: str
    market_id: str
    outcome_id: str
    user_id: str
    side: str
    type: str
    price: None | float
    quantity: float
    filled_quantity: float
    status: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        market_id = self.market_id

        outcome_id = self.outcome_id

        user_id = self.user_id

        side = self.side

        type = self.type

        price: None | float
        price = self.price

        quantity = self.quantity

        filled_quantity = self.filled_quantity

        status = self.status

        created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "marketId": market_id,
                "outcomeId": outcome_id,
                "userId": user_id,
                "side": side,
                "type": type,
                "price": price,
                "quantity": quantity,
                "filledQuantity": filled_quantity,
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

        user_id = d.pop("userId")

        side = d.pop("side")

        type = d.pop("type")

        def _parse_price(data: object) -> None | float:
            if data is None:
                return data
            return cast(None | float, data)

        price = _parse_price(d.pop("price"))

        quantity = d.pop("quantity")

        filled_quantity = d.pop("filledQuantity")

        status = d.pop("status")

        created_at = d.pop("createdAt")

        get_api_v1_orders_response_200_orders_item = cls(
            id=id,
            market_id=market_id,
            outcome_id=outcome_id,
            user_id=user_id,
            side=side,
            type=type,
            price=price,
            quantity=quantity,
            filled_quantity=filled_quantity,
            status=status,
            created_at=created_at,
        )

        return get_api_v1_orders_response_200_orders_item
