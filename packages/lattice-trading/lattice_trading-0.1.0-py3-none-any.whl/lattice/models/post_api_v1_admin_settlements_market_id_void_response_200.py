
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.post_api_v1_admin_settlements_market_id_void_response_200_status import (
    PostApiV1AdminSettlementsMarketIdVoidResponse200Status,
)

T = TypeVar("T", bound="PostApiV1AdminSettlementsMarketIdVoidResponse200")


@_attrs_define
class PostApiV1AdminSettlementsMarketIdVoidResponse200:
    """
    Attributes:
        market_id (str):
        status (PostApiV1AdminSettlementsMarketIdVoidResponse200Status):
        orders_refunded (float):
        positions_cleared (float):
        total_refunded (float):
        voided_at (str):
    """

    market_id: str
    status: PostApiV1AdminSettlementsMarketIdVoidResponse200Status
    orders_refunded: float
    positions_cleared: float
    total_refunded: float
    voided_at: str

    def to_dict(self) -> dict[str, Any]:
        market_id = self.market_id

        status = self.status.value

        orders_refunded = self.orders_refunded

        positions_cleared = self.positions_cleared

        total_refunded = self.total_refunded

        voided_at = self.voided_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "marketId": market_id,
                "status": status,
                "ordersRefunded": orders_refunded,
                "positionsCleared": positions_cleared,
                "totalRefunded": total_refunded,
                "voidedAt": voided_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        market_id = d.pop("marketId")

        status = PostApiV1AdminSettlementsMarketIdVoidResponse200Status(d.pop("status"))

        orders_refunded = d.pop("ordersRefunded")

        positions_cleared = d.pop("positionsCleared")

        total_refunded = d.pop("totalRefunded")

        voided_at = d.pop("voidedAt")

        post_api_v1_admin_settlements_market_id_void_response_200 = cls(
            market_id=market_id,
            status=status,
            orders_refunded=orders_refunded,
            positions_cleared=positions_cleared,
            total_refunded=total_refunded,
            voided_at=voided_at,
        )

        return post_api_v1_admin_settlements_market_id_void_response_200
