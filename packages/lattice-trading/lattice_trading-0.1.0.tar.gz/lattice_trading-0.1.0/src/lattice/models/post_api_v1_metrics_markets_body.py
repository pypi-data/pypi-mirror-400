
from __future__ import annotations

from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostApiV1MetricsMarketsBody")


@_attrs_define
class PostApiV1MetricsMarketsBody:
    """
    Attributes:
        market_ids (List[str]):
    """

    market_ids: list[str]

    def to_dict(self) -> dict[str, Any]:
        market_ids = self.market_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "marketIds": market_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        market_ids = cast(list[str], d.pop("marketIds"))

        post_api_v1_metrics_markets_body = cls(
            market_ids=market_ids,
        )

        return post_api_v1_metrics_markets_body
