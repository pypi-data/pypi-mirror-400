
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1TenantsConfigResponse200Api")


@_attrs_define
class GetApiV1TenantsConfigResponse200Api:
    """
    Attributes:
        base_url (str):
        ws_url (str):
    """

    base_url: str
    ws_url: str

    def to_dict(self) -> dict[str, Any]:
        base_url = self.base_url

        ws_url = self.ws_url

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "baseUrl": base_url,
                "wsUrl": ws_url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        base_url = d.pop("baseUrl")

        ws_url = d.pop("wsUrl")

        get_api_v1_tenants_config_response_200_api = cls(
            base_url=base_url,
            ws_url=ws_url,
        )

        return get_api_v1_tenants_config_response_200_api
