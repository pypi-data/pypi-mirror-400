
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.get_health_ready_response_503_status import GetHealthReadyResponse503Status
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_health_ready_response_503_checks import GetHealthReadyResponse503Checks


T = TypeVar("T", bound="GetHealthReadyResponse503")


@_attrs_define
class GetHealthReadyResponse503:
    """
    Attributes:
        status (GetHealthReadyResponse503Status):
        version (str):
        timestamp (datetime.datetime):
        checks (GetHealthReadyResponse503Checks):
        active_requests (Union[Unset, float]):
    """

    status: GetHealthReadyResponse503Status
    version: str
    timestamp: datetime.datetime
    checks: "GetHealthReadyResponse503Checks"
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
        from ..models.get_health_ready_response_503_checks import GetHealthReadyResponse503Checks

        d = src_dict.copy()
        status = GetHealthReadyResponse503Status(d.pop("status"))

        version = d.pop("version")

        timestamp = isoparse(d.pop("timestamp"))

        checks = GetHealthReadyResponse503Checks.from_dict(d.pop("checks"))

        active_requests = d.pop("activeRequests", UNSET)

        get_health_ready_response_503 = cls(
            status=status,
            version=version,
            timestamp=timestamp,
            checks=checks,
            active_requests=active_requests,
        )

        return get_health_ready_response_503
