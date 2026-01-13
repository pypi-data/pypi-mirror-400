
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetHealthMetricsResponse200Memory")


@_attrs_define
class GetHealthMetricsResponse200Memory:
    """
    Attributes:
        rss (float):
        heap_total (float):
        heap_used (float):
        external (float):
        array_buffers (Union[Unset, float]):
    """

    rss: float
    heap_total: float
    heap_used: float
    external: float
    array_buffers: Unset | float = UNSET

    def to_dict(self) -> dict[str, Any]:
        rss = self.rss

        heap_total = self.heap_total

        heap_used = self.heap_used

        external = self.external

        array_buffers = self.array_buffers

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "rss": rss,
                "heapTotal": heap_total,
                "heapUsed": heap_used,
                "external": external,
            }
        )
        if array_buffers is not UNSET:
            field_dict["arrayBuffers"] = array_buffers

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        rss = d.pop("rss")

        heap_total = d.pop("heapTotal")

        heap_used = d.pop("heapUsed")

        external = d.pop("external")

        array_buffers = d.pop("arrayBuffers", UNSET)

        get_health_metrics_response_200_memory = cls(
            rss=rss,
            heap_total=heap_total,
            heap_used=heap_used,
            external=external,
            array_buffers=array_buffers,
        )

        return get_health_metrics_response_200_memory
