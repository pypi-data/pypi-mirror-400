
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostApiV1AdminMarketsMarketIdResolveResponse200")


@_attrs_define
class PostApiV1AdminMarketsMarketIdResolveResponse200:
    """
    Attributes:
        market_id (str):
        status (str):
        winning_outcome_id (str):
        settled_at (str):
    """

    market_id: str
    status: str
    winning_outcome_id: str
    settled_at: str

    def to_dict(self) -> dict[str, Any]:
        market_id = self.market_id

        status = self.status

        winning_outcome_id = self.winning_outcome_id

        settled_at = self.settled_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "marketId": market_id,
                "status": status,
                "winningOutcomeId": winning_outcome_id,
                "settledAt": settled_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        market_id = d.pop("marketId")

        status = d.pop("status")

        winning_outcome_id = d.pop("winningOutcomeId")

        settled_at = d.pop("settledAt")

        post_api_v1_admin_markets_market_id_resolve_response_200 = cls(
            market_id=market_id,
            status=status,
            winning_outcome_id=winning_outcome_id,
            settled_at=settled_at,
        )

        return post_api_v1_admin_markets_market_id_resolve_response_200
