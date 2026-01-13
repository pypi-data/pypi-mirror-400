
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_admin_settlements_market_id_history_response_200_events_item_data import (
        GetApiV1AdminSettlementsMarketIdHistoryResponse200EventsItemData,
    )


T = TypeVar("T", bound="GetApiV1AdminSettlementsMarketIdHistoryResponse200EventsItem")


@_attrs_define
class GetApiV1AdminSettlementsMarketIdHistoryResponse200EventsItem:
    """
    Attributes:
        type (str):
        created_at (str):
        data (GetApiV1AdminSettlementsMarketIdHistoryResponse200EventsItemData):
    """

    type: str
    created_at: str
    data: "GetApiV1AdminSettlementsMarketIdHistoryResponse200EventsItemData"

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
        from ..models.get_api_v1_admin_settlements_market_id_history_response_200_events_item_data import (
            GetApiV1AdminSettlementsMarketIdHistoryResponse200EventsItemData,
        )

        d = src_dict.copy()
        type = d.pop("type")

        created_at = d.pop("createdAt")

        data = GetApiV1AdminSettlementsMarketIdHistoryResponse200EventsItemData.from_dict(d.pop("data"))

        get_api_v1_admin_settlements_market_id_history_response_200_events_item = cls(
            type=type,
            created_at=created_at,
            data=data,
        )

        return get_api_v1_admin_settlements_market_id_history_response_200_events_item
