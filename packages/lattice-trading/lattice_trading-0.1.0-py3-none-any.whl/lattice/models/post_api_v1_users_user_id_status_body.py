
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.post_api_v1_users_user_id_status_body_status import PostApiV1UsersUserIdStatusBodyStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="PostApiV1UsersUserIdStatusBody")


@_attrs_define
class PostApiV1UsersUserIdStatusBody:
    """
    Attributes:
        status (PostApiV1UsersUserIdStatusBodyStatus):
        reason (Union[Unset, str]):
    """

    status: PostApiV1UsersUserIdStatusBodyStatus
    reason: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        reason = self.reason

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "status": status,
            }
        )
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        status = PostApiV1UsersUserIdStatusBodyStatus(d.pop("status"))

        reason = d.pop("reason", UNSET)

        post_api_v1_users_user_id_status_body = cls(
            status=status,
            reason=reason,
        )

        return post_api_v1_users_user_id_status_body
