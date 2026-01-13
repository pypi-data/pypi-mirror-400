
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_api_v1_users_response_201_account import PostApiV1UsersResponse201Account


T = TypeVar("T", bound="PostApiV1UsersResponse201")


@_attrs_define
class PostApiV1UsersResponse201:
    """
    Attributes:
        id (str):
        email (str):
        display_name (Union[None, str]):
        kyc_status (str):
        status (str):
        account (PostApiV1UsersResponse201Account):
        created_at (str):
    """

    id: str
    email: str
    display_name: None | str
    kyc_status: str
    status: str
    account: "PostApiV1UsersResponse201Account"
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        email = self.email

        display_name: None | str
        display_name = self.display_name

        kyc_status = self.kyc_status

        status = self.status

        account = self.account.to_dict()

        created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "email": email,
                "displayName": display_name,
                "kycStatus": kyc_status,
                "status": status,
                "account": account,
                "createdAt": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.post_api_v1_users_response_201_account import PostApiV1UsersResponse201Account

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

        account = PostApiV1UsersResponse201Account.from_dict(d.pop("account"))

        created_at = d.pop("createdAt")

        post_api_v1_users_response_201 = cls(
            id=id,
            email=email,
            display_name=display_name,
            kyc_status=kyc_status,
            status=status,
            account=account,
            created_at=created_at,
        )

        return post_api_v1_users_response_201
