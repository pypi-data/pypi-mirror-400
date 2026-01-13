
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_health_metrics_response_200_cpu import GetHealthMetricsResponse200Cpu
    from ..models.get_health_metrics_response_200_memory import GetHealthMetricsResponse200Memory


T = TypeVar("T", bound="GetHealthMetricsResponse200")


@_attrs_define
class GetHealthMetricsResponse200:
    """
    Attributes:
        uptime (float):
        memory (GetHealthMetricsResponse200Memory):
        cpu (GetHealthMetricsResponse200Cpu):
    """

    uptime: float
    memory: "GetHealthMetricsResponse200Memory"
    cpu: "GetHealthMetricsResponse200Cpu"

    def to_dict(self) -> dict[str, Any]:
        uptime = self.uptime

        memory = self.memory.to_dict()

        cpu = self.cpu.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "uptime": uptime,
                "memory": memory,
                "cpu": cpu,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_health_metrics_response_200_cpu import GetHealthMetricsResponse200Cpu
        from ..models.get_health_metrics_response_200_memory import GetHealthMetricsResponse200Memory

        d = src_dict.copy()
        uptime = d.pop("uptime")

        memory = GetHealthMetricsResponse200Memory.from_dict(d.pop("memory"))

        cpu = GetHealthMetricsResponse200Cpu.from_dict(d.pop("cpu"))

        get_health_metrics_response_200 = cls(
            uptime=uptime,
            memory=memory,
            cpu=cpu,
        )

        return get_health_metrics_response_200
