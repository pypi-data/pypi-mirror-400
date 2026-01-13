
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1TenantsConfigResponse200Features")


@_attrs_define
class GetApiV1TenantsConfigResponse200Features:
    """
    Attributes:
        registration (bool):
        social_login (bool):
        kyc (bool):
        deposits (bool):
        withdrawals (bool):
    """

    registration: bool
    social_login: bool
    kyc: bool
    deposits: bool
    withdrawals: bool

    def to_dict(self) -> dict[str, Any]:
        registration = self.registration

        social_login = self.social_login

        kyc = self.kyc

        deposits = self.deposits

        withdrawals = self.withdrawals

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "registration": registration,
                "socialLogin": social_login,
                "kyc": kyc,
                "deposits": deposits,
                "withdrawals": withdrawals,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        registration = d.pop("registration")

        social_login = d.pop("socialLogin")

        kyc = d.pop("kyc")

        deposits = d.pop("deposits")

        withdrawals = d.pop("withdrawals")

        get_api_v1_tenants_config_response_200_features = cls(
            registration=registration,
            social_login=social_login,
            kyc=kyc,
            deposits=deposits,
            withdrawals=withdrawals,
        )

        return get_api_v1_tenants_config_response_200_features
