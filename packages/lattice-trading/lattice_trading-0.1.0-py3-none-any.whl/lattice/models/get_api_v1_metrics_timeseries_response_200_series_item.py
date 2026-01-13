
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1MetricsTimeseriesResponse200SeriesItem")


@_attrs_define
class GetApiV1MetricsTimeseriesResponse200SeriesItem:
    """
    Attributes:
        timestamp (str):
        value (float):
    """

    timestamp: str
    value: float

    def to_dict(self) -> dict[str, Any]:
        timestamp = self.timestamp

        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "timestamp": timestamp,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        timestamp = d.pop("timestamp")

        value = d.pop("value")

        get_api_v1_metrics_timeseries_response_200_series_item = cls(
            timestamp=timestamp,
            value=value,
        )

        return get_api_v1_metrics_timeseries_response_200_series_item
