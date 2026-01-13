
from __future__ import annotations

from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.get_api_v1_positions_response_200_positions_item_status import (
    GetApiV1PositionsResponse200PositionsItemStatus,
)

T = TypeVar("T", bound="GetApiV1PositionsResponse200PositionsItem")


@_attrs_define
class GetApiV1PositionsResponse200PositionsItem:
    """
    Attributes:
        id (str):
        market_id (str):
        outcome_id (str):
        user_id (str):
        market_title (Union[None, str]):
        outcome_name (Union[None, str]):
        quantity (float):
        average_cost (float):
        realized_pnl (float):
        unrealized_pnl (Union[None, float]):
        current_price (Union[None, float]):
        status (GetApiV1PositionsResponse200PositionsItemStatus):
        updated_at (str):
    """

    id: str
    market_id: str
    outcome_id: str
    user_id: str
    market_title: None | str
    outcome_name: None | str
    quantity: float
    average_cost: float
    realized_pnl: float
    unrealized_pnl: None | float
    current_price: None | float
    status: GetApiV1PositionsResponse200PositionsItemStatus
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        market_id = self.market_id

        outcome_id = self.outcome_id

        user_id = self.user_id

        market_title: None | str
        market_title = self.market_title

        outcome_name: None | str
        outcome_name = self.outcome_name

        quantity = self.quantity

        average_cost = self.average_cost

        realized_pnl = self.realized_pnl

        unrealized_pnl: None | float
        unrealized_pnl = self.unrealized_pnl

        current_price: None | float
        current_price = self.current_price

        status = self.status.value

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "marketId": market_id,
                "outcomeId": outcome_id,
                "userId": user_id,
                "marketTitle": market_title,
                "outcomeName": outcome_name,
                "quantity": quantity,
                "averageCost": average_cost,
                "realizedPnl": realized_pnl,
                "unrealizedPnl": unrealized_pnl,
                "currentPrice": current_price,
                "status": status,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        market_id = d.pop("marketId")

        outcome_id = d.pop("outcomeId")

        user_id = d.pop("userId")

        def _parse_market_title(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        market_title = _parse_market_title(d.pop("marketTitle"))

        def _parse_outcome_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        outcome_name = _parse_outcome_name(d.pop("outcomeName"))

        quantity = d.pop("quantity")

        average_cost = d.pop("averageCost")

        realized_pnl = d.pop("realizedPnl")

        def _parse_unrealized_pnl(data: object) -> None | float:
            if data is None:
                return data
            return cast(None | float, data)

        unrealized_pnl = _parse_unrealized_pnl(d.pop("unrealizedPnl"))

        def _parse_current_price(data: object) -> None | float:
            if data is None:
                return data
            return cast(None | float, data)

        current_price = _parse_current_price(d.pop("currentPrice"))

        status = GetApiV1PositionsResponse200PositionsItemStatus(d.pop("status"))

        updated_at = d.pop("updatedAt")

        get_api_v1_positions_response_200_positions_item = cls(
            id=id,
            market_id=market_id,
            outcome_id=outcome_id,
            user_id=user_id,
            market_title=market_title,
            outcome_name=outcome_name,
            quantity=quantity,
            average_cost=average_cost,
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl,
            current_price=current_price,
            status=status,
            updated_at=updated_at,
        )

        return get_api_v1_positions_response_200_positions_item
