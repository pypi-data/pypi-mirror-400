
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.post_api_v1_users_user_id_kyc_body_status import PostApiV1UsersUserIdKycBodyStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="PostApiV1UsersUserIdKycBody")


@_attrs_define
class PostApiV1UsersUserIdKycBody:
    """
    Attributes:
        status (PostApiV1UsersUserIdKycBodyStatus):
        notes (Union[Unset, str]):
    """

    status: PostApiV1UsersUserIdKycBodyStatus
    notes: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        notes = self.notes

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "status": status,
            }
        )
        if notes is not UNSET:
            field_dict["notes"] = notes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        status = PostApiV1UsersUserIdKycBodyStatus(d.pop("status"))

        notes = d.pop("notes", UNSET)

        post_api_v1_users_user_id_kyc_body = cls(
            status=status,
            notes=notes,
        )

        return post_api_v1_users_user_id_kyc_body
