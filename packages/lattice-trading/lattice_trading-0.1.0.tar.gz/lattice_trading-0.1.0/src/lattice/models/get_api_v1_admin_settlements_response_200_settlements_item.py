
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_admin_settlements_response_200_settlements_item_data import (
        GetApiV1AdminSettlementsResponse200SettlementsItemData,
    )


T = TypeVar("T", bound="GetApiV1AdminSettlementsResponse200SettlementsItem")


@_attrs_define
class GetApiV1AdminSettlementsResponse200SettlementsItem:
    """
    Attributes:
        type (str):
        created_at (str):
        data (GetApiV1AdminSettlementsResponse200SettlementsItemData):
    """

    type: str
    created_at: str
    data: "GetApiV1AdminSettlementsResponse200SettlementsItemData"

    def to_dict(self) -> dict[str, Any]:
        type = self.type

        created_at = self.created_at

        data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "type": type,
                "createdAt": created_at,
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_admin_settlements_response_200_settlements_item_data import (
            GetApiV1AdminSettlementsResponse200SettlementsItemData,
        )

        d = src_dict.copy()
        type = d.pop("type")

        created_at = d.pop("createdAt")

        data = GetApiV1AdminSettlementsResponse200SettlementsItemData.from_dict(d.pop("data"))

        get_api_v1_admin_settlements_response_200_settlements_item = cls(
            type=type,
            created_at=created_at,
            data=data,
        )

        return get_api_v1_admin_settlements_response_200_settlements_item
