
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetApiV1TemplatesResponse200ItemDefaultSettings")


@_attrs_define
class GetApiV1TemplatesResponse200ItemDefaultSettings:
    """
    Attributes:
        close_date (Union[Unset, str]):
        resolution (Union[Unset, str]):
        visibility (Union[Unset, str]):
    """

    close_date: Unset | str = UNSET
    resolution: Unset | str = UNSET
    visibility: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        close_date = self.close_date

        resolution = self.resolution

        visibility = self.visibility

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if close_date is not UNSET:
            field_dict["closeDate"] = close_date
        if resolution is not UNSET:
            field_dict["resolution"] = resolution
        if visibility is not UNSET:
            field_dict["visibility"] = visibility

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        close_date = d.pop("closeDate", UNSET)

        resolution = d.pop("resolution", UNSET)

        visibility = d.pop("visibility", UNSET)

        get_api_v1_templates_response_200_item_default_settings = cls(
            close_date=close_date,
            resolution=resolution,
            visibility=visibility,
        )

        return get_api_v1_templates_response_200_item_default_settings
