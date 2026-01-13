
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostApiV1UsersUserIdKycResponse200")


@_attrs_define
class PostApiV1UsersUserIdKycResponse200:
    """
    Attributes:
        id (str):
        kyc_status (str):
        updated_at (str):
    """

    id: str
    kyc_status: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        kyc_status = self.kyc_status

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "kycStatus": kyc_status,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        kyc_status = d.pop("kycStatus")

        updated_at = d.pop("updatedAt")

        post_api_v1_users_user_id_kyc_response_200 = cls(
            id=id,
            kyc_status=kyc_status,
            updated_at=updated_at,
        )

        return post_api_v1_users_user_id_kyc_response_200
