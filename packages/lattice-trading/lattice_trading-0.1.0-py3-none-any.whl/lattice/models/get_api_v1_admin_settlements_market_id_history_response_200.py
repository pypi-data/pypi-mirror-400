
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_admin_settlements_market_id_history_response_200_events_item import (
        GetApiV1AdminSettlementsMarketIdHistoryResponse200EventsItem,
    )


T = TypeVar("T", bound="GetApiV1AdminSettlementsMarketIdHistoryResponse200")


@_attrs_define
class GetApiV1AdminSettlementsMarketIdHistoryResponse200:
    """
    Attributes:
        events (List['GetApiV1AdminSettlementsMarketIdHistoryResponse200EventsItem']):
    """

    events: list["GetApiV1AdminSettlementsMarketIdHistoryResponse200EventsItem"]

    def to_dict(self) -> dict[str, Any]:
        events = []
        for events_item_data in self.events:
            events_item = events_item_data.to_dict()
            events.append(events_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "events": events,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_admin_settlements_market_id_history_response_200_events_item import (
            GetApiV1AdminSettlementsMarketIdHistoryResponse200EventsItem,
        )

        d = src_dict.copy()
        events = []
        _events = d.pop("events")
        for events_item_data in _events:
            events_item = GetApiV1AdminSettlementsMarketIdHistoryResponse200EventsItem.from_dict(events_item_data)

            events.append(events_item)

        get_api_v1_admin_settlements_market_id_history_response_200 = cls(
            events=events,
        )

        return get_api_v1_admin_settlements_market_id_history_response_200
