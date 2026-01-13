
from __future__ import annotations

from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1MarketsResponse200MarketsItemOutcomesItem")


@_attrs_define
class GetApiV1MarketsResponse200MarketsItemOutcomesItem:
    """
    Attributes:
        id (str):
        name (str):
        last_price (Union[None, float]):
    """

    id: str
    name: str
    last_price: None | float

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        last_price: None | float
        last_price = self.last_price

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "name": name,
                "lastPrice": last_price,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        def _parse_last_price(data: object) -> None | float:
            if data is None:
                return data
            return cast(None | float, data)

        last_price = _parse_last_price(d.pop("lastPrice"))

        get_api_v1_markets_response_200_markets_item_outcomes_item = cls(
            id=id,
            name=name,
            last_price=last_price,
        )

        return get_api_v1_markets_response_200_markets_item_outcomes_item
