
from __future__ import annotations

from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1MarketsMarketIdResponse200OutcomesItem")


@_attrs_define
class GetApiV1MarketsMarketIdResponse200OutcomesItem:
    """
    Attributes:
        id (str):
        name (str):
        description (Union[None, str]):
        index (float):
    """

    id: str
    name: str
    description: None | str
    index: float

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        description: None | str
        description = self.description

        index = self.index

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "index": index,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        index = d.pop("index")

        get_api_v1_markets_market_id_response_200_outcomes_item = cls(
            id=id,
            name=name,
            description=description,
            index=index,
        )

        return get_api_v1_markets_market_id_response_200_outcomes_item
