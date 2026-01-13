
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.post_api_v1_orders_body_side import PostApiV1OrdersBodySide
from ..models.post_api_v1_orders_body_time_in_force import PostApiV1OrdersBodyTimeInForce
from ..models.post_api_v1_orders_body_type import PostApiV1OrdersBodyType
from ..types import UNSET, Unset

T = TypeVar("T", bound="PostApiV1OrdersBody")


@_attrs_define
class PostApiV1OrdersBody:
    """
    Attributes:
        market_id (str):
        outcome_id (str):
        side (PostApiV1OrdersBodySide):
        type (PostApiV1OrdersBodyType):
        quantity (int):
        price (Union[Unset, int]):
        time_in_force (Union[Unset, PostApiV1OrdersBodyTimeInForce]):  Default: PostApiV1OrdersBodyTimeInForce.GTC.
    """

    market_id: str
    outcome_id: str
    side: PostApiV1OrdersBodySide
    type: PostApiV1OrdersBodyType
    quantity: int
    price: Unset | int = UNSET
    time_in_force: Unset | PostApiV1OrdersBodyTimeInForce = PostApiV1OrdersBodyTimeInForce.GTC

    def to_dict(self) -> dict[str, Any]:
        market_id = self.market_id

        outcome_id = self.outcome_id

        side = self.side.value

        type = self.type.value

        quantity = self.quantity

        price = self.price

        time_in_force: Unset | str = UNSET
        if not isinstance(self.time_in_force, Unset):
            time_in_force = self.time_in_force.value

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "marketId": market_id,
                "outcomeId": outcome_id,
                "side": side,
                "type": type,
                "quantity": quantity,
            }
        )
        if price is not UNSET:
            field_dict["price"] = price
        if time_in_force is not UNSET:
            field_dict["timeInForce"] = time_in_force

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        market_id = d.pop("marketId")

        outcome_id = d.pop("outcomeId")

        side = PostApiV1OrdersBodySide(d.pop("side"))

        type = PostApiV1OrdersBodyType(d.pop("type"))

        quantity = d.pop("quantity")

        price = d.pop("price", UNSET)

        _time_in_force = d.pop("timeInForce", UNSET)
        time_in_force: Unset | PostApiV1OrdersBodyTimeInForce
        if isinstance(_time_in_force, Unset):
            time_in_force = UNSET
        else:
            time_in_force = PostApiV1OrdersBodyTimeInForce(_time_in_force)

        post_api_v1_orders_body = cls(
            market_id=market_id,
            outcome_id=outcome_id,
            side=side,
            type=type,
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
        )

        return post_api_v1_orders_body
