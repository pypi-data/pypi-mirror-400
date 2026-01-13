
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostApiV1UsersUserIdDepositResponse200")


@_attrs_define
class PostApiV1UsersUserIdDepositResponse200:
    """
    Attributes:
        account_id (str):
        new_balance (float):
        deposited_at (str):
    """

    account_id: str
    new_balance: float
    deposited_at: str

    def to_dict(self) -> dict[str, Any]:
        account_id = self.account_id

        new_balance = self.new_balance

        deposited_at = self.deposited_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "accountId": account_id,
                "newBalance": new_balance,
                "depositedAt": deposited_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        account_id = d.pop("accountId")

        new_balance = d.pop("newBalance")

        deposited_at = d.pop("depositedAt")

        post_api_v1_users_user_id_deposit_response_200 = cls(
            account_id=account_id,
            new_balance=new_balance,
            deposited_at=deposited_at,
        )

        return post_api_v1_users_user_id_deposit_response_200
