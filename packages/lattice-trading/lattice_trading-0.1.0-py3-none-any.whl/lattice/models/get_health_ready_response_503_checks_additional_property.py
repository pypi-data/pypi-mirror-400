
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.get_health_ready_response_503_checks_additional_property_status import (
    GetHealthReadyResponse503ChecksAdditionalPropertyStatus,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetHealthReadyResponse503ChecksAdditionalProperty")


@_attrs_define
class GetHealthReadyResponse503ChecksAdditionalProperty:
    """
    Attributes:
        status (GetHealthReadyResponse503ChecksAdditionalPropertyStatus):
        latency_ms (Union[Unset, float]):
        message (Union[Unset, str]):
    """

    status: GetHealthReadyResponse503ChecksAdditionalPropertyStatus
    latency_ms: Unset | float = UNSET
    message: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        latency_ms = self.latency_ms

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "status": status,
            }
        )
        if latency_ms is not UNSET:
            field_dict["latencyMs"] = latency_ms
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        status = GetHealthReadyResponse503ChecksAdditionalPropertyStatus(d.pop("status"))

        latency_ms = d.pop("latencyMs", UNSET)

        message = d.pop("message", UNSET)

        get_health_ready_response_503_checks_additional_property = cls(
            status=status,
            latency_ms=latency_ms,
            message=message,
        )

        return get_health_ready_response_503_checks_additional_property
