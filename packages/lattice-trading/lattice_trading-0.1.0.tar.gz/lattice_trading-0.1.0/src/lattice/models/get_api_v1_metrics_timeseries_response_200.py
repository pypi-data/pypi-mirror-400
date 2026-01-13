
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..models.get_api_v1_metrics_timeseries_response_200_interval import GetApiV1MetricsTimeseriesResponse200Interval
from ..models.get_api_v1_metrics_timeseries_response_200_metric import GetApiV1MetricsTimeseriesResponse200Metric

if TYPE_CHECKING:
    from ..models.get_api_v1_metrics_timeseries_response_200_series_item import (
        GetApiV1MetricsTimeseriesResponse200SeriesItem,
    )


T = TypeVar("T", bound="GetApiV1MetricsTimeseriesResponse200")


@_attrs_define
class GetApiV1MetricsTimeseriesResponse200:
    """
    Attributes:
        metric (GetApiV1MetricsTimeseriesResponse200Metric):
        interval (GetApiV1MetricsTimeseriesResponse200Interval):
        start (str):
        end (str):
        series (List['GetApiV1MetricsTimeseriesResponse200SeriesItem']):
    """

    metric: GetApiV1MetricsTimeseriesResponse200Metric
    interval: GetApiV1MetricsTimeseriesResponse200Interval
    start: str
    end: str
    series: list["GetApiV1MetricsTimeseriesResponse200SeriesItem"]

    def to_dict(self) -> dict[str, Any]:
        metric = self.metric.value

        interval = self.interval.value

        start = self.start

        end = self.end

        series = []
        for series_item_data in self.series:
            series_item = series_item_data.to_dict()
            series.append(series_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "metric": metric,
                "interval": interval,
                "start": start,
                "end": end,
                "series": series,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_metrics_timeseries_response_200_series_item import (
            GetApiV1MetricsTimeseriesResponse200SeriesItem,
        )

        d = src_dict.copy()
        metric = GetApiV1MetricsTimeseriesResponse200Metric(d.pop("metric"))

        interval = GetApiV1MetricsTimeseriesResponse200Interval(d.pop("interval"))

        start = d.pop("start")

        end = d.pop("end")

        series = []
        _series = d.pop("series")
        for series_item_data in _series:
            series_item = GetApiV1MetricsTimeseriesResponse200SeriesItem.from_dict(series_item_data)

            series.append(series_item)

        get_api_v1_metrics_timeseries_response_200 = cls(
            metric=metric,
            interval=interval,
            start=start,
            end=end,
            series=series,
        )

        return get_api_v1_metrics_timeseries_response_200
