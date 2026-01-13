
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_admin_alerts_stats_response_200_by_severity import (
        GetApiV1AdminAlertsStatsResponse200BySeverity,
    )
    from ..models.get_api_v1_admin_alerts_stats_response_200_by_status import (
        GetApiV1AdminAlertsStatsResponse200ByStatus,
    )
    from ..models.get_api_v1_admin_alerts_stats_response_200_by_type import GetApiV1AdminAlertsStatsResponse200ByType
    from ..models.get_api_v1_admin_alerts_stats_response_200_trend import GetApiV1AdminAlertsStatsResponse200Trend


T = TypeVar("T", bound="GetApiV1AdminAlertsStatsResponse200")


@_attrs_define
class GetApiV1AdminAlertsStatsResponse200:
    """
    Attributes:
        total_open (float):
        by_severity (GetApiV1AdminAlertsStatsResponse200BySeverity):
        by_type (GetApiV1AdminAlertsStatsResponse200ByType):
        by_status (GetApiV1AdminAlertsStatsResponse200ByStatus):
        trend (GetApiV1AdminAlertsStatsResponse200Trend):
    """

    total_open: float
    by_severity: "GetApiV1AdminAlertsStatsResponse200BySeverity"
    by_type: "GetApiV1AdminAlertsStatsResponse200ByType"
    by_status: "GetApiV1AdminAlertsStatsResponse200ByStatus"
    trend: "GetApiV1AdminAlertsStatsResponse200Trend"

    def to_dict(self) -> dict[str, Any]:
        total_open = self.total_open

        by_severity = self.by_severity.to_dict()

        by_type = self.by_type.to_dict()

        by_status = self.by_status.to_dict()

        trend = self.trend.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "totalOpen": total_open,
                "bySeverity": by_severity,
                "byType": by_type,
                "byStatus": by_status,
                "trend": trend,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_admin_alerts_stats_response_200_by_severity import (
            GetApiV1AdminAlertsStatsResponse200BySeverity,
        )
        from ..models.get_api_v1_admin_alerts_stats_response_200_by_status import (
            GetApiV1AdminAlertsStatsResponse200ByStatus,
        )
        from ..models.get_api_v1_admin_alerts_stats_response_200_by_type import (
            GetApiV1AdminAlertsStatsResponse200ByType,
        )
        from ..models.get_api_v1_admin_alerts_stats_response_200_trend import GetApiV1AdminAlertsStatsResponse200Trend

        d = src_dict.copy()
        total_open = d.pop("totalOpen")

        by_severity = GetApiV1AdminAlertsStatsResponse200BySeverity.from_dict(d.pop("bySeverity"))

        by_type = GetApiV1AdminAlertsStatsResponse200ByType.from_dict(d.pop("byType"))

        by_status = GetApiV1AdminAlertsStatsResponse200ByStatus.from_dict(d.pop("byStatus"))

        trend = GetApiV1AdminAlertsStatsResponse200Trend.from_dict(d.pop("trend"))

        get_api_v1_admin_alerts_stats_response_200 = cls(
            total_open=total_open,
            by_severity=by_severity,
            by_type=by_type,
            by_status=by_status,
            trend=trend,
        )

        return get_api_v1_admin_alerts_stats_response_200
