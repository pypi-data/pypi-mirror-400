
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetApiV1AdminSettlementsMarketIdResponse200")


@_attrs_define
class GetApiV1AdminSettlementsMarketIdResponse200:
    """
    Attributes:
        market_id (str):
        status (str):
        position_count (float):
        total_long_positions (float):
        total_short_positions (float):
        estimated_payouts (float):
        winning_outcome_id (Union[Unset, str]):
        resolved_at (Union[Unset, str]):
    """

    market_id: str
    status: str
    position_count: float
    total_long_positions: float
    total_short_positions: float
    estimated_payouts: float
    winning_outcome_id: Unset | str = UNSET
    resolved_at: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        market_id = self.market_id

        status = self.status

        position_count = self.position_count

        total_long_positions = self.total_long_positions

        total_short_positions = self.total_short_positions

        estimated_payouts = self.estimated_payouts

        winning_outcome_id = self.winning_outcome_id

        resolved_at = self.resolved_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "marketId": market_id,
                "status": status,
                "positionCount": position_count,
                "totalLongPositions": total_long_positions,
                "totalShortPositions": total_short_positions,
                "estimatedPayouts": estimated_payouts,
            }
        )
        if winning_outcome_id is not UNSET:
            field_dict["winningOutcomeId"] = winning_outcome_id
        if resolved_at is not UNSET:
            field_dict["resolvedAt"] = resolved_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        market_id = d.pop("marketId")

        status = d.pop("status")

        position_count = d.pop("positionCount")

        total_long_positions = d.pop("totalLongPositions")

        total_short_positions = d.pop("totalShortPositions")

        estimated_payouts = d.pop("estimatedPayouts")

        winning_outcome_id = d.pop("winningOutcomeId", UNSET)

        resolved_at = d.pop("resolvedAt", UNSET)

        get_api_v1_admin_settlements_market_id_response_200 = cls(
            market_id=market_id,
            status=status,
            position_count=position_count,
            total_long_positions=total_long_positions,
            total_short_positions=total_short_positions,
            estimated_payouts=estimated_payouts,
            winning_outcome_id=winning_outcome_id,
            resolved_at=resolved_at,
        )

        return get_api_v1_admin_settlements_market_id_response_200
