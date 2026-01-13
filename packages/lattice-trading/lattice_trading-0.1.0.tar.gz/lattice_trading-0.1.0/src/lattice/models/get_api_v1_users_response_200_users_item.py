
from __future__ import annotations

from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1UsersResponse200UsersItem")


@_attrs_define
class GetApiV1UsersResponse200UsersItem:
    """
    Attributes:
        id (str):
        email (str):
        display_name (Union[None, str]):
        kyc_status (str):
        status (str):
        created_at (str):
    """

    id: str
    email: str
    display_name: None | str
    kyc_status: str
    status: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        email = self.email

        display_name: None | str
        display_name = self.display_name

        kyc_status = self.kyc_status

        status = self.status

        created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "email": email,
                "displayName": display_name,
                "kycStatus": kyc_status,
                "status": status,
                "createdAt": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        email = d.pop("email")

        def _parse_display_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        display_name = _parse_display_name(d.pop("displayName"))

        kyc_status = d.pop("kycStatus")

        status = d.pop("status")

        created_at = d.pop("createdAt")

        get_api_v1_users_response_200_users_item = cls(
            id=id,
            email=email,
            display_name=display_name,
            kyc_status=kyc_status,
            status=status,
            created_at=created_at,
        )

        return get_api_v1_users_response_200_users_item
