
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostApiV1UsersResponse201Account")


@_attrs_define
class PostApiV1UsersResponse201Account:
    """
    Attributes:
        id (str):
        balance (float):
    """

    id: str
    balance: float

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        balance = self.balance

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "balance": balance,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        balance = d.pop("balance")

        post_api_v1_users_response_201_account = cls(
            id=id,
            balance=balance,
        )

        return post_api_v1_users_response_201_account
