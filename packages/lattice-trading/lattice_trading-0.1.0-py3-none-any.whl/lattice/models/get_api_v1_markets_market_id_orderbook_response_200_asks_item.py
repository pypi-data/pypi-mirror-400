
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1MarketsMarketIdOrderbookResponse200AsksItem")


@_attrs_define
class GetApiV1MarketsMarketIdOrderbookResponse200AsksItem:
    """
    Attributes:
        price (float):
        size (float):
        order_count (float):
    """

    price: float
    size: float
    order_count: float

    def to_dict(self) -> dict[str, Any]:
        price = self.price

        size = self.size

        order_count = self.order_count

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "price": price,
                "size": size,
                "orderCount": order_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        price = d.pop("price")

        size = d.pop("size")

        order_count = d.pop("orderCount")

        get_api_v1_markets_market_id_orderbook_response_200_asks_item = cls(
            price=price,
            size=size,
            order_count=order_count,
        )

        return get_api_v1_markets_market_id_orderbook_response_200_asks_item
