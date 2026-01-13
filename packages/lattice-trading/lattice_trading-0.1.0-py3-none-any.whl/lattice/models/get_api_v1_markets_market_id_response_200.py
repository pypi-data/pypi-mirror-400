
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_markets_market_id_response_200_metadata import GetApiV1MarketsMarketIdResponse200Metadata
    from ..models.get_api_v1_markets_market_id_response_200_outcomes_item import (
        GetApiV1MarketsMarketIdResponse200OutcomesItem,
    )


T = TypeVar("T", bound="GetApiV1MarketsMarketIdResponse200")


@_attrs_define
class GetApiV1MarketsMarketIdResponse200:
    """
    Attributes:
        id (str):
        title (str):
        description (Union[None, str]):
        type (str):
        status (str):
        trading_ends_at (Union[None, str]):
        winning_outcome_id (Union[None, str]):
        metadata (GetApiV1MarketsMarketIdResponse200Metadata):
        outcomes (List['GetApiV1MarketsMarketIdResponse200OutcomesItem']):
        created_at (str):
        updated_at (str):
    """

    id: str
    title: str
    description: None | str
    type: str
    status: str
    trading_ends_at: None | str
    winning_outcome_id: None | str
    metadata: "GetApiV1MarketsMarketIdResponse200Metadata"
    outcomes: list["GetApiV1MarketsMarketIdResponse200OutcomesItem"]
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        description: None | str
        description = self.description

        type = self.type

        status = self.status

        trading_ends_at: None | str
        trading_ends_at = self.trading_ends_at

        winning_outcome_id: None | str
        winning_outcome_id = self.winning_outcome_id

        metadata = self.metadata.to_dict()

        outcomes = []
        for outcomes_item_data in self.outcomes:
            outcomes_item = outcomes_item_data.to_dict()
            outcomes.append(outcomes_item)

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "title": title,
                "description": description,
                "type": type,
                "status": status,
                "tradingEndsAt": trading_ends_at,
                "winningOutcomeId": winning_outcome_id,
                "metadata": metadata,
                "outcomes": outcomes,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_markets_market_id_response_200_metadata import (
            GetApiV1MarketsMarketIdResponse200Metadata,
        )
        from ..models.get_api_v1_markets_market_id_response_200_outcomes_item import (
            GetApiV1MarketsMarketIdResponse200OutcomesItem,
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

        def _parse_trading_ends_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        trading_ends_at = _parse_trading_ends_at(d.pop("tradingEndsAt"))

        def _parse_winning_outcome_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        winning_outcome_id = _parse_winning_outcome_id(d.pop("winningOutcomeId"))

        metadata = GetApiV1MarketsMarketIdResponse200Metadata.from_dict(d.pop("metadata"))

        outcomes = []
        _outcomes = d.pop("outcomes")
        for outcomes_item_data in _outcomes:
            outcomes_item = GetApiV1MarketsMarketIdResponse200OutcomesItem.from_dict(outcomes_item_data)

            outcomes.append(outcomes_item)

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        get_api_v1_markets_market_id_response_200 = cls(
            id=id,
            title=title,
            description=description,
            type=type,
            status=status,
            trading_ends_at=trading_ends_at,
            winning_outcome_id=winning_outcome_id,
            metadata=metadata,
            outcomes=outcomes,
            created_at=created_at,
            updated_at=updated_at,
        )

        return get_api_v1_markets_market_id_response_200
