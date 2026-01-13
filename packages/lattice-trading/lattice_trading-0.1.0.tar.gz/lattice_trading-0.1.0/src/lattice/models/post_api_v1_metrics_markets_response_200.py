
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_api_v1_metrics_markets_response_200_metrics_item import (
        PostApiV1MetricsMarketsResponse200MetricsItem,
    )


T = TypeVar("T", bound="PostApiV1MetricsMarketsResponse200")


@_attrs_define
class PostApiV1MetricsMarketsResponse200:
    """
    Attributes:
        metrics (List['PostApiV1MetricsMarketsResponse200MetricsItem']):
    """

    metrics: list["PostApiV1MetricsMarketsResponse200MetricsItem"]

    def to_dict(self) -> dict[str, Any]:
        metrics = []
        for metrics_item_data in self.metrics:
            metrics_item = metrics_item_data.to_dict()
            metrics.append(metrics_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "metrics": metrics,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.post_api_v1_metrics_markets_response_200_metrics_item import (
            PostApiV1MetricsMarketsResponse200MetricsItem,
        )

        d = src_dict.copy()
        metrics = []
        _metrics = d.pop("metrics")
        for metrics_item_data in _metrics:
            metrics_item = PostApiV1MetricsMarketsResponse200MetricsItem.from_dict(metrics_item_data)

            metrics.append(metrics_item)

        post_api_v1_metrics_markets_response_200 = cls(
            metrics=metrics,
        )

        return post_api_v1_metrics_markets_response_200
