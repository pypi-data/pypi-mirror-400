
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostApiV1MarketsMarketIdResolveBody")


@_attrs_define
class PostApiV1MarketsMarketIdResolveBody:
    """
    Attributes:
        winning_outcome_id (str):
    """

    winning_outcome_id: str

    def to_dict(self) -> dict[str, Any]:
        winning_outcome_id = self.winning_outcome_id

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "winningOutcomeId": winning_outcome_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        winning_outcome_id = d.pop("winningOutcomeId")

        post_api_v1_markets_market_id_resolve_body = cls(
            winning_outcome_id=winning_outcome_id,
        )

        return post_api_v1_markets_market_id_resolve_body
