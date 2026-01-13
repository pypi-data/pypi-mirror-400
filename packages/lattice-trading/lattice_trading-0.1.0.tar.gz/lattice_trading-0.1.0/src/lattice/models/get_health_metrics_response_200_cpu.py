
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetHealthMetricsResponse200Cpu")


@_attrs_define
class GetHealthMetricsResponse200Cpu:
    """
    Attributes:
        user (float):
        system (float):
    """

    user: float
    system: float

    def to_dict(self) -> dict[str, Any]:
        user = self.user

        system = self.system

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "user": user,
                "system": system,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        user = d.pop("user")

        system = d.pop("system")

        get_health_metrics_response_200_cpu = cls(
            user=user,
            system=system,
        )

        return get_health_metrics_response_200_cpu
