
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1MetricsTimeseriesResponse400")


@_attrs_define
class GetApiV1MetricsTimeseriesResponse400:
    """
    Attributes:
        error (str):
        code (str):
    """

    error: str
    code: str

    def to_dict(self) -> dict[str, Any]:
        error = self.error

        code = self.code

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "error": error,
                "code": code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        error = d.pop("error")

        code = d.pop("code")

        get_api_v1_metrics_timeseries_response_400 = cls(
            error=error,
            code=code,
        )

        return get_api_v1_metrics_timeseries_response_400
