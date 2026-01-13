
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_admin_settlements_response_200_settlements_item import (
        GetApiV1AdminSettlementsResponse200SettlementsItem,
    )


T = TypeVar("T", bound="GetApiV1AdminSettlementsResponse200")


@_attrs_define
class GetApiV1AdminSettlementsResponse200:
    """
    Attributes:
        settlements (List['GetApiV1AdminSettlementsResponse200SettlementsItem']):
    """

    settlements: list["GetApiV1AdminSettlementsResponse200SettlementsItem"]

    def to_dict(self) -> dict[str, Any]:
        settlements = []
        for settlements_item_data in self.settlements:
            settlements_item = settlements_item_data.to_dict()
            settlements.append(settlements_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "settlements": settlements,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_admin_settlements_response_200_settlements_item import (
            GetApiV1AdminSettlementsResponse200SettlementsItem,
        )

        d = src_dict.copy()
        settlements = []
        _settlements = d.pop("settlements")
        for settlements_item_data in _settlements:
            settlements_item = GetApiV1AdminSettlementsResponse200SettlementsItem.from_dict(settlements_item_data)

            settlements.append(settlements_item)

        get_api_v1_admin_settlements_response_200 = cls(
            settlements=settlements,
        )

        return get_api_v1_admin_settlements_response_200
