
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1MarketsMarketIdPositionsResponse200PositionsItem")


@_attrs_define
class GetApiV1MarketsMarketIdPositionsResponse200PositionsItem:
    """
    Attributes:
        outcome_id (str):
        outcome_name (str):
        quantity (float):
        average_cost (float):
        value (float):
    """

    outcome_id: str
    outcome_name: str
    quantity: float
    average_cost: float
    value: float

    def to_dict(self) -> dict[str, Any]:
        outcome_id = self.outcome_id

        outcome_name = self.outcome_name

        quantity = self.quantity

        average_cost = self.average_cost

        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "outcomeId": outcome_id,
                "outcomeName": outcome_name,
                "quantity": quantity,
                "averageCost": average_cost,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        outcome_id = d.pop("outcomeId")

        outcome_name = d.pop("outcomeName")

        quantity = d.pop("quantity")

        average_cost = d.pop("averageCost")

        value = d.pop("value")

        get_api_v1_markets_market_id_positions_response_200_positions_item = cls(
            outcome_id=outcome_id,
            outcome_name=outcome_name,
            quantity=quantity,
            average_cost=average_cost,
            value=value,
        )

        return get_api_v1_markets_market_id_positions_response_200_positions_item
