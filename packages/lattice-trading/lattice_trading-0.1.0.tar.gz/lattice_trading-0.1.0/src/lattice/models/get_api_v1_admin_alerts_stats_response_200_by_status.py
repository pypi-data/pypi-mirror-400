
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1AdminAlertsStatsResponse200ByStatus")


@_attrs_define
class GetApiV1AdminAlertsStatsResponse200ByStatus:
    """
    Attributes:
        open_ (float):
        investigating (float):
        resolved (float):
        dismissed (float):
    """

    open_: float
    investigating: float
    resolved: float
    dismissed: float

    def to_dict(self) -> dict[str, Any]:
        open_ = self.open_

        investigating = self.investigating

        resolved = self.resolved

        dismissed = self.dismissed

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "open": open_,
                "investigating": investigating,
                "resolved": resolved,
                "dismissed": dismissed,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        open_ = d.pop("open")

        investigating = d.pop("investigating")

        resolved = d.pop("resolved")

        dismissed = d.pop("dismissed")

        get_api_v1_admin_alerts_stats_response_200_by_status = cls(
            open_=open_,
            investigating=investigating,
            resolved=resolved,
            dismissed=dismissed,
        )

        return get_api_v1_admin_alerts_stats_response_200_by_status
