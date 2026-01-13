
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_positions_response_200_positions_item import GetApiV1PositionsResponse200PositionsItem


T = TypeVar("T", bound="GetApiV1PositionsResponse200")


@_attrs_define
class GetApiV1PositionsResponse200:
    """
    Attributes:
        positions (List['GetApiV1PositionsResponse200PositionsItem']):
        total (float):
        limit (float):
        offset (float):
    """

    positions: list["GetApiV1PositionsResponse200PositionsItem"]
    total: float
    limit: float
    offset: float

    def to_dict(self) -> dict[str, Any]:
        positions = []
        for positions_item_data in self.positions:
            positions_item = positions_item_data.to_dict()
            positions.append(positions_item)

        total = self.total

        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "positions": positions,
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_positions_response_200_positions_item import GetApiV1PositionsResponse200PositionsItem

        d = src_dict.copy()
        positions = []
        _positions = d.pop("positions")
        for positions_item_data in _positions:
            positions_item = GetApiV1PositionsResponse200PositionsItem.from_dict(positions_item_data)

            positions.append(positions_item)

        total = d.pop("total")

        limit = d.pop("limit")

        offset = d.pop("offset")

        get_api_v1_positions_response_200 = cls(
            positions=positions,
            total=total,
            limit=limit,
            offset=offset,
        )

        return get_api_v1_positions_response_200
