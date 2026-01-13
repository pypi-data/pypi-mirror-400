
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_markets_response_200_markets_item import GetApiV1MarketsResponse200MarketsItem


T = TypeVar("T", bound="GetApiV1MarketsResponse200")


@_attrs_define
class GetApiV1MarketsResponse200:
    """
    Attributes:
        markets (List['GetApiV1MarketsResponse200MarketsItem']):
        total (float):
        limit (float):
        offset (float):
    """

    markets: list["GetApiV1MarketsResponse200MarketsItem"]
    total: float
    limit: float
    offset: float

    def to_dict(self) -> dict[str, Any]:
        markets = []
        for markets_item_data in self.markets:
            markets_item = markets_item_data.to_dict()
            markets.append(markets_item)

        total = self.total

        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "markets": markets,
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_markets_response_200_markets_item import GetApiV1MarketsResponse200MarketsItem

        d = src_dict.copy()
        markets = []
        _markets = d.pop("markets")
        for markets_item_data in _markets:
            markets_item = GetApiV1MarketsResponse200MarketsItem.from_dict(markets_item_data)

            markets.append(markets_item)

        total = d.pop("total")

        limit = d.pop("limit")

        offset = d.pop("offset")

        get_api_v1_markets_response_200 = cls(
            markets=markets,
            total=total,
            limit=limit,
            offset=offset,
        )

        return get_api_v1_markets_response_200
