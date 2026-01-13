
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_markets_market_id_positions_response_200_positions_item import (
        GetApiV1MarketsMarketIdPositionsResponse200PositionsItem,
    )


T = TypeVar("T", bound="GetApiV1MarketsMarketIdPositionsResponse200")


@_attrs_define
class GetApiV1MarketsMarketIdPositionsResponse200:
    """
    Attributes:
        positions (List['GetApiV1MarketsMarketIdPositionsResponse200PositionsItem']):
        total_value (float):
    """

    positions: list["GetApiV1MarketsMarketIdPositionsResponse200PositionsItem"]
    total_value: float

    def to_dict(self) -> dict[str, Any]:
        positions = []
        for positions_item_data in self.positions:
            positions_item = positions_item_data.to_dict()
            positions.append(positions_item)

        total_value = self.total_value

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "positions": positions,
                "totalValue": total_value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_markets_market_id_positions_response_200_positions_item import (
            GetApiV1MarketsMarketIdPositionsResponse200PositionsItem,
        )

        d = src_dict.copy()
        positions = []
        _positions = d.pop("positions")
        for positions_item_data in _positions:
            positions_item = GetApiV1MarketsMarketIdPositionsResponse200PositionsItem.from_dict(positions_item_data)

            positions.append(positions_item)

        total_value = d.pop("totalValue")

        get_api_v1_markets_market_id_positions_response_200 = cls(
            positions=positions,
            total_value=total_value,
        )

        return get_api_v1_markets_market_id_positions_response_200
