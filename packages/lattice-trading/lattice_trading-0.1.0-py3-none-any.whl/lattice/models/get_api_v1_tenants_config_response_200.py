
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_tenants_config_response_200_api import GetApiV1TenantsConfigResponse200Api
    from ..models.get_api_v1_tenants_config_response_200_branding import GetApiV1TenantsConfigResponse200Branding
    from ..models.get_api_v1_tenants_config_response_200_features import GetApiV1TenantsConfigResponse200Features
    from ..models.get_api_v1_tenants_config_response_200_legal import GetApiV1TenantsConfigResponse200Legal


T = TypeVar("T", bound="GetApiV1TenantsConfigResponse200")


@_attrs_define
class GetApiV1TenantsConfigResponse200:
    """
    Attributes:
        id (str):
        name (str):
        domain (str):
        branding (GetApiV1TenantsConfigResponse200Branding):
        features (GetApiV1TenantsConfigResponse200Features):
        api (GetApiV1TenantsConfigResponse200Api):
        legal (GetApiV1TenantsConfigResponse200Legal):
    """

    id: str
    name: str
    domain: str
    branding: "GetApiV1TenantsConfigResponse200Branding"
    features: "GetApiV1TenantsConfigResponse200Features"
    api: "GetApiV1TenantsConfigResponse200Api"
    legal: "GetApiV1TenantsConfigResponse200Legal"

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        domain = self.domain

        branding = self.branding.to_dict()

        features = self.features.to_dict()

        api = self.api.to_dict()

        legal = self.legal.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "name": name,
                "domain": domain,
                "branding": branding,
                "features": features,
                "api": api,
                "legal": legal,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_tenants_config_response_200_api import GetApiV1TenantsConfigResponse200Api
        from ..models.get_api_v1_tenants_config_response_200_branding import GetApiV1TenantsConfigResponse200Branding
        from ..models.get_api_v1_tenants_config_response_200_features import GetApiV1TenantsConfigResponse200Features
        from ..models.get_api_v1_tenants_config_response_200_legal import GetApiV1TenantsConfigResponse200Legal

        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        domain = d.pop("domain")

        branding = GetApiV1TenantsConfigResponse200Branding.from_dict(d.pop("branding"))

        features = GetApiV1TenantsConfigResponse200Features.from_dict(d.pop("features"))

        api = GetApiV1TenantsConfigResponse200Api.from_dict(d.pop("api"))

        legal = GetApiV1TenantsConfigResponse200Legal.from_dict(d.pop("legal"))

        get_api_v1_tenants_config_response_200 = cls(
            id=id,
            name=name,
            domain=domain,
            branding=branding,
            features=features,
            api=api,
            legal=legal,
        )

        return get_api_v1_tenants_config_response_200
