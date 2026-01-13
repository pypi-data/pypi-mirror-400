
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="DeleteApiV1OrdersOrderIdResponse200")


@_attrs_define
class DeleteApiV1OrdersOrderIdResponse200:
    """
    Attributes:
        id (str):
        status (str):
        cancelled_at (str):
    """

    id: str
    status: str
    cancelled_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        status = self.status

        cancelled_at = self.cancelled_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "status": status,
                "cancelledAt": cancelled_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        status = d.pop("status")

        cancelled_at = d.pop("cancelledAt")

        delete_api_v1_orders_order_id_response_200 = cls(
            id=id,
            status=status,
            cancelled_at=cancelled_at,
        )

        return delete_api_v1_orders_order_id_response_200
