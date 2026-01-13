
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_users_user_id_response_200_account_type_0 import GetApiV1UsersUserIdResponse200AccountType0
    from ..models.get_api_v1_users_user_id_response_200_metadata import GetApiV1UsersUserIdResponse200Metadata


T = TypeVar("T", bound="GetApiV1UsersUserIdResponse200")


@_attrs_define
class GetApiV1UsersUserIdResponse200:
    """
    Attributes:
        id (str):
        external_id (Union[None, str]):
        email (str):
        display_name (Union[None, str]):
        kyc_status (str):
        status (str):
        metadata (GetApiV1UsersUserIdResponse200Metadata):
        account (Union['GetApiV1UsersUserIdResponse200AccountType0', None]):
        created_at (str):
        updated_at (str):
    """

    id: str
    external_id: None | str
    email: str
    display_name: None | str
    kyc_status: str
    status: str
    metadata: "GetApiV1UsersUserIdResponse200Metadata"
    account: Union["GetApiV1UsersUserIdResponse200AccountType0", None]
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_api_v1_users_user_id_response_200_account_type_0 import (
            GetApiV1UsersUserIdResponse200AccountType0,
        )

        id = self.id

        external_id: None | str
        external_id = self.external_id

        email = self.email

        display_name: None | str
        display_name = self.display_name

        kyc_status = self.kyc_status

        status = self.status

        metadata = self.metadata.to_dict()

        account: dict[str, Any] | None
        if isinstance(self.account, GetApiV1UsersUserIdResponse200AccountType0):
            account = self.account.to_dict()
        else:
            account = self.account

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "externalId": external_id,
                "email": email,
                "displayName": display_name,
                "kycStatus": kyc_status,
                "status": status,
                "metadata": metadata,
                "account": account,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_users_user_id_response_200_account_type_0 import (
            GetApiV1UsersUserIdResponse200AccountType0,
        )
        from ..models.get_api_v1_users_user_id_response_200_metadata import GetApiV1UsersUserIdResponse200Metadata

        d = src_dict.copy()
        id = d.pop("id")

        def _parse_external_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        external_id = _parse_external_id(d.pop("externalId"))

        email = d.pop("email")

        def _parse_display_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        display_name = _parse_display_name(d.pop("displayName"))

        kyc_status = d.pop("kycStatus")

        status = d.pop("status")

        metadata = GetApiV1UsersUserIdResponse200Metadata.from_dict(d.pop("metadata"))

        def _parse_account(data: object) -> Union["GetApiV1UsersUserIdResponse200AccountType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                account_type_0 = GetApiV1UsersUserIdResponse200AccountType0.from_dict(data)

                return account_type_0
            except:  # noqa: E722
                pass
            return cast(Union["GetApiV1UsersUserIdResponse200AccountType0", None], data)

        account = _parse_account(d.pop("account"))

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        get_api_v1_users_user_id_response_200 = cls(
            id=id,
            external_id=external_id,
            email=email,
            display_name=display_name,
            kyc_status=kyc_status,
            status=status,
            metadata=metadata,
            account=account,
            created_at=created_at,
            updated_at=updated_at,
        )

        return get_api_v1_users_user_id_response_200
