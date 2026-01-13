
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.post_api_v1_admin_settlements_market_id_resolve_response_200_status import (
    PostApiV1AdminSettlementsMarketIdResolveResponse200Status,
)

T = TypeVar("T", bound="PostApiV1AdminSettlementsMarketIdResolveResponse200")


@_attrs_define
class PostApiV1AdminSettlementsMarketIdResolveResponse200:
    """
    Attributes:
        market_id (str):
        status (PostApiV1AdminSettlementsMarketIdResolveResponse200Status):
        winning_outcome_id (str):
        total_payouts (float):
        positions_settled (float):
        settled_at (str):
    """

    market_id: str
    status: PostApiV1AdminSettlementsMarketIdResolveResponse200Status
    winning_outcome_id: str
    total_payouts: float
    positions_settled: float
    settled_at: str

    def to_dict(self) -> dict[str, Any]:
        market_id = self.market_id

        status = self.status.value

        winning_outcome_id = self.winning_outcome_id

        total_payouts = self.total_payouts

        positions_settled = self.positions_settled

        settled_at = self.settled_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "marketId": market_id,
                "status": status,
                "winningOutcomeId": winning_outcome_id,
                "totalPayouts": total_payouts,
                "positionsSettled": positions_settled,
                "settledAt": settled_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        market_id = d.pop("marketId")

        status = PostApiV1AdminSettlementsMarketIdResolveResponse200Status(d.pop("status"))

        winning_outcome_id = d.pop("winningOutcomeId")

        total_payouts = d.pop("totalPayouts")

        positions_settled = d.pop("positionsSettled")

        settled_at = d.pop("settledAt")

        post_api_v1_admin_settlements_market_id_resolve_response_200 = cls(
            market_id=market_id,
            status=status,
            winning_outcome_id=winning_outcome_id,
            total_payouts=total_payouts,
            positions_settled=positions_settled,
            settled_at=settled_at,
        )

        return post_api_v1_admin_settlements_market_id_resolve_response_200
