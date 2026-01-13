
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1TenantsConfigResponse200Legal")


@_attrs_define
class GetApiV1TenantsConfigResponse200Legal:
    """
    Attributes:
        terms_url (str):
        privacy_url (str):
        company_name (str):
    """

    terms_url: str
    privacy_url: str
    company_name: str

    def to_dict(self) -> dict[str, Any]:
        terms_url = self.terms_url

        privacy_url = self.privacy_url

        company_name = self.company_name

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "termsUrl": terms_url,
                "privacyUrl": privacy_url,
                "companyName": company_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        terms_url = d.pop("termsUrl")

        privacy_url = d.pop("privacyUrl")

        company_name = d.pop("companyName")

        get_api_v1_tenants_config_response_200_legal = cls(
            terms_url=terms_url,
            privacy_url=privacy_url,
            company_name=company_name,
        )

        return get_api_v1_tenants_config_response_200_legal
