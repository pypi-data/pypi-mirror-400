
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1AdminAlertsStatsResponse200Trend")


@_attrs_define
class GetApiV1AdminAlertsStatsResponse200Trend:
    """
    Attributes:
        last24h (float):
        last7d (float):
        last30d (float):
    """

    last24h: float
    last7d: float
    last30d: float

    def to_dict(self) -> dict[str, Any]:
        last24h = self.last24h

        last7d = self.last7d

        last30d = self.last30d

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "last24h": last24h,
                "last7d": last7d,
                "last30d": last30d,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        last24h = d.pop("last24h")

        last7d = d.pop("last7d")

        last30d = d.pop("last30d")

        get_api_v1_admin_alerts_stats_response_200_trend = cls(
            last24h=last24h,
            last7d=last7d,
            last30d=last30d,
        )

        return get_api_v1_admin_alerts_stats_response_200_trend
