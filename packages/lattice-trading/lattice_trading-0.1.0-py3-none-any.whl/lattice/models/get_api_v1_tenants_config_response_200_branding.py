
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1TenantsConfigResponse200Branding")


@_attrs_define
class GetApiV1TenantsConfigResponse200Branding:
    """
    Attributes:
        logo (str):
        logo_alt (str):
        favicon (str):
        primary_color (str):
        secondary_color (str):
        accent_color (str):
    """

    logo: str
    logo_alt: str
    favicon: str
    primary_color: str
    secondary_color: str
    accent_color: str

    def to_dict(self) -> dict[str, Any]:
        logo = self.logo

        logo_alt = self.logo_alt

        favicon = self.favicon

        primary_color = self.primary_color

        secondary_color = self.secondary_color

        accent_color = self.accent_color

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "logo": logo,
                "logoAlt": logo_alt,
                "favicon": favicon,
                "primaryColor": primary_color,
                "secondaryColor": secondary_color,
                "accentColor": accent_color,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        logo = d.pop("logo")

        logo_alt = d.pop("logoAlt")

        favicon = d.pop("favicon")

        primary_color = d.pop("primaryColor")

        secondary_color = d.pop("secondaryColor")

        accent_color = d.pop("accentColor")

        get_api_v1_tenants_config_response_200_branding = cls(
            logo=logo,
            logo_alt=logo_alt,
            favicon=favicon,
            primary_color=primary_color,
            secondary_color=secondary_color,
            accent_color=accent_color,
        )

        return get_api_v1_tenants_config_response_200_branding
