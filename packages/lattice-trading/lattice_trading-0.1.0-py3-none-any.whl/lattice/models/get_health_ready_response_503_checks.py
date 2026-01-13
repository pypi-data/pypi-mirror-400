
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_health_ready_response_503_checks_additional_property import (
        GetHealthReadyResponse503ChecksAdditionalProperty,
    )


T = TypeVar("T", bound="GetHealthReadyResponse503Checks")


@_attrs_define
class GetHealthReadyResponse503Checks:
    """ """

    additional_properties: dict[str, "GetHealthReadyResponse503ChecksAdditionalProperty"] = _attrs_field(
        init=False, factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_health_ready_response_503_checks_additional_property import (
            GetHealthReadyResponse503ChecksAdditionalProperty,
        )

        d = src_dict.copy()
        get_health_ready_response_503_checks = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = GetHealthReadyResponse503ChecksAdditionalProperty.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        get_health_ready_response_503_checks.additional_properties = additional_properties
        return get_health_ready_response_503_checks

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> "GetHealthReadyResponse503ChecksAdditionalProperty":
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: "GetHealthReadyResponse503ChecksAdditionalProperty") -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
