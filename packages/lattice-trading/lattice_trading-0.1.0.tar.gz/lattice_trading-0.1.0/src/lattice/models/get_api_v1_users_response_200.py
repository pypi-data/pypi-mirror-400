
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_users_response_200_users_item import GetApiV1UsersResponse200UsersItem


T = TypeVar("T", bound="GetApiV1UsersResponse200")


@_attrs_define
class GetApiV1UsersResponse200:
    """
    Attributes:
        users (List['GetApiV1UsersResponse200UsersItem']):
        total (float):
        limit (float):
        offset (float):
    """

    users: list["GetApiV1UsersResponse200UsersItem"]
    total: float
    limit: float
    offset: float

    def to_dict(self) -> dict[str, Any]:
        users = []
        for users_item_data in self.users:
            users_item = users_item_data.to_dict()
            users.append(users_item)

        total = self.total

        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "users": users,
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_users_response_200_users_item import GetApiV1UsersResponse200UsersItem

        d = src_dict.copy()
        users = []
        _users = d.pop("users")
        for users_item_data in _users:
            users_item = GetApiV1UsersResponse200UsersItem.from_dict(users_item_data)

            users.append(users_item)

        total = d.pop("total")

        limit = d.pop("limit")

        offset = d.pop("offset")

        get_api_v1_users_response_200 = cls(
            users=users,
            total=total,
            limit=limit,
            offset=offset,
        )

        return get_api_v1_users_response_200
