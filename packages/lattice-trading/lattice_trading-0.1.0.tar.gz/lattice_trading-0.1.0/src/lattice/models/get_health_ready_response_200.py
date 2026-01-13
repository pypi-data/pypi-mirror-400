
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.get_health_ready_response_200_status import GetHealthReadyResponse200Status
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_health_ready_response_200_checks import GetHealthReadyResponse200Checks


T = TypeVar("T", bound="GetHealthReadyResponse200")


@_attrs_define
class GetHealthReadyResponse200:
    """
    Attributes:
        status (GetHealthReadyResponse200Status):
        version (str):
        timestamp (datetime.datetime):
        checks (GetHealthReadyResponse200Checks):
        active_requests (Union[Unset, float]):
    """

    status: GetHealthReadyResponse200Status
    version: str
    timestamp: datetime.datetime
    checks: "GetHealthReadyResponse200Checks"
    active_requests: Unset | float = UNSET

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        version = self.version

        timestamp = self.timestamp.isoformat()

        checks = self.checks.to_dict()

        active_requests = self.active_requests

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "status": status,
                "version": version,
                "timestamp": timestamp,
                "checks": checks,
            }
        )
        if active_requests is not UNSET:
            field_dict["activeRequests"] = active_requests

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_health_ready_response_200_checks import GetHealthReadyResponse200Checks

        d = src_dict.copy()
        status = GetHealthReadyResponse200Status(d.pop("status"))

        version = d.pop("version")

        timestamp = isoparse(d.pop("timestamp"))

        checks = GetHealthReadyResponse200Checks.from_dict(d.pop("checks"))

        active_requests = d.pop("activeRequests", UNSET)

        get_health_ready_response_200 = cls(
            status=status,
            version=version,
            timestamp=timestamp,
            checks=checks,
            active_requests=active_requests,
        )

        return get_health_ready_response_200
