
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostApiV1UsersUserIdStatusResponse200")


@_attrs_define
class PostApiV1UsersUserIdStatusResponse200:
    """
    Attributes:
        id (str):
        status (str):
        previous_status (str):
        updated_at (str):
    """

    id: str
    status: str
    previous_status: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        status = self.status

        previous_status = self.previous_status

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "status": status,
                "previousStatus": previous_status,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        status = d.pop("status")

        previous_status = d.pop("previousStatus")

        updated_at = d.pop("updatedAt")

        post_api_v1_users_user_id_status_response_200 = cls(
            id=id,
            status=status,
            previous_status=previous_status,
            updated_at=updated_at,
        )

        return post_api_v1_users_user_id_status_response_200
