
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GetApiV1AdminSettlementsMarketIdHistoryResponse200EventsItemData")


@_attrs_define
class GetApiV1AdminSettlementsMarketIdHistoryResponse200EventsItemData:
    """ """

    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        get_api_v1_admin_settlements_market_id_history_response_200_events_item_data = cls()

        get_api_v1_admin_settlements_market_id_history_response_200_events_item_data.additional_properties = d
        return get_api_v1_admin_settlements_market_id_history_response_200_events_item_data

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
