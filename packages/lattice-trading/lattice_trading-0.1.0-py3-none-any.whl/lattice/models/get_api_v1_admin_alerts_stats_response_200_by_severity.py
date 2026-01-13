
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1AdminAlertsStatsResponse200BySeverity")


@_attrs_define
class GetApiV1AdminAlertsStatsResponse200BySeverity:
    """
    Attributes:
        low (float):
        medium (float):
        high (float):
        critical (float):
    """

    low: float
    medium: float
    high: float
    critical: float

    def to_dict(self) -> dict[str, Any]:
        low = self.low

        medium = self.medium

        high = self.high

        critical = self.critical

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "low": low,
                "medium": medium,
                "high": high,
                "critical": critical,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        low = d.pop("low")

        medium = d.pop("medium")

        high = d.pop("high")

        critical = d.pop("critical")

        get_api_v1_admin_alerts_stats_response_200_by_severity = cls(
            low=low,
            medium=medium,
            high=high,
            critical=critical,
        )

        return get_api_v1_admin_alerts_stats_response_200_by_severity
