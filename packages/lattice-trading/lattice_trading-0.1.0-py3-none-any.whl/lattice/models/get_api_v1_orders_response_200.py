
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_orders_response_200_orders_item import GetApiV1OrdersResponse200OrdersItem


T = TypeVar("T", bound="GetApiV1OrdersResponse200")


@_attrs_define
class GetApiV1OrdersResponse200:
    """
    Attributes:
        orders (List['GetApiV1OrdersResponse200OrdersItem']):
        total (float):
        limit (float):
        offset (float):
    """

    orders: list["GetApiV1OrdersResponse200OrdersItem"]
    total: float
    limit: float
    offset: float

    def to_dict(self) -> dict[str, Any]:
        orders = []
        for orders_item_data in self.orders:
            orders_item = orders_item_data.to_dict()
            orders.append(orders_item)

        total = self.total

        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "orders": orders,
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_orders_response_200_orders_item import GetApiV1OrdersResponse200OrdersItem

        d = src_dict.copy()
        orders = []
        _orders = d.pop("orders")
        for orders_item_data in _orders:
            orders_item = GetApiV1OrdersResponse200OrdersItem.from_dict(orders_item_data)

            orders.append(orders_item)

        total = d.pop("total")

        limit = d.pop("limit")

        offset = d.pop("offset")

        get_api_v1_orders_response_200 = cls(
            orders=orders,
            total=total,
            limit=limit,
            offset=offset,
        )

        return get_api_v1_orders_response_200
