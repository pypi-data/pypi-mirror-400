
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_markets_response_200_markets_item_outcomes_item import (
        GetApiV1MarketsResponse200MarketsItemOutcomesItem,
    )


T = TypeVar("T", bound="GetApiV1MarketsResponse200MarketsItem")


@_attrs_define
class GetApiV1MarketsResponse200MarketsItem:
    """
    Attributes:
        id (str):
        title (str):
        description (Union[None, str]):
        type (str):
        status (str):
        category (Union[None, str]):
        trading_ends_at (Union[None, str]):
        outcomes (List['GetApiV1MarketsResponse200MarketsItemOutcomesItem']):
        volume_cents (float):
        last_price (Union[None, float]):
        created_at (str):
    """

    id: str
    title: str
    description: None | str
    type: str
    status: str
    category: None | str
    trading_ends_at: None | str
    outcomes: list["GetApiV1MarketsResponse200MarketsItemOutcomesItem"]
    volume_cents: float
    last_price: None | float
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        description: None | str
        description = self.description

        type = self.type

        status = self.status

        category: None | str
        category = self.category

        trading_ends_at: None | str
        trading_ends_at = self.trading_ends_at

        outcomes = []
        for outcomes_item_data in self.outcomes:
            outcomes_item = outcomes_item_data.to_dict()
            outcomes.append(outcomes_item)

        volume_cents = self.volume_cents

        last_price: None | float
        last_price = self.last_price

        created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "title": title,
                "description": description,
                "type": type,
                "status": status,
                "category": category,
                "tradingEndsAt": trading_ends_at,
                "outcomes": outcomes,
                "volumeCents": volume_cents,
                "lastPrice": last_price,
                "createdAt": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_markets_response_200_markets_item_outcomes_item import (
            GetApiV1MarketsResponse200MarketsItemOutcomesItem,
        )

        d = src_dict.copy()
        id = d.pop("id")

        title = d.pop("title")

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        type = d.pop("type")

        status = d.pop("status")

        def _parse_category(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        category = _parse_category(d.pop("category"))

        def _parse_trading_ends_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        trading_ends_at = _parse_trading_ends_at(d.pop("tradingEndsAt"))

        outcomes = []
        _outcomes = d.pop("outcomes")
        for outcomes_item_data in _outcomes:
            outcomes_item = GetApiV1MarketsResponse200MarketsItemOutcomesItem.from_dict(outcomes_item_data)

            outcomes.append(outcomes_item)

        volume_cents = d.pop("volumeCents")

        def _parse_last_price(data: object) -> None | float:
            if data is None:
                return data
            return cast(None | float, data)

        last_price = _parse_last_price(d.pop("lastPrice"))

        created_at = d.pop("createdAt")

        get_api_v1_markets_response_200_markets_item = cls(
            id=id,
            title=title,
            description=description,
            type=type,
            status=status,
            category=category,
            trading_ends_at=trading_ends_at,
            outcomes=outcomes,
            volume_cents=volume_cents,
            last_price=last_price,
            created_at=created_at,
        )

        return get_api_v1_markets_response_200_markets_item
