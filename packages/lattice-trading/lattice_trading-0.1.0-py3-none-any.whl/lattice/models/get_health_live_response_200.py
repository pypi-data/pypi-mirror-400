
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.get_health_live_response_200_status import GetHealthLiveResponse200Status

T = TypeVar("T", bound="GetHealthLiveResponse200")


@_attrs_define
class GetHealthLiveResponse200:
    """
    Attributes:
        status (GetHealthLiveResponse200Status):
    """

    status: GetHealthLiveResponse200Status

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        status = GetHealthLiveResponse200Status(d.pop("status"))

        get_health_live_response_200 = cls(
            status=status,
        )

        return get_health_live_response_200
