
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostApiV1MarketsMarketIdResolveResponse200")


@_attrs_define
class PostApiV1MarketsMarketIdResolveResponse200:
    """
    Attributes:
        id (str):
        status (str):
        winning_outcome_id (str):
        resolved_at (str):
    """

    id: str
    status: str
    winning_outcome_id: str
    resolved_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        status = self.status

        winning_outcome_id = self.winning_outcome_id

        resolved_at = self.resolved_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "status": status,
                "winningOutcomeId": winning_outcome_id,
                "resolvedAt": resolved_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        status = d.pop("status")

        winning_outcome_id = d.pop("winningOutcomeId")

        resolved_at = d.pop("resolvedAt")

        post_api_v1_markets_market_id_resolve_response_200 = cls(
            id=id,
            status=status,
            winning_outcome_id=winning_outcome_id,
            resolved_at=resolved_at,
        )

        return post_api_v1_markets_market_id_resolve_response_200
