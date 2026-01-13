
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostApiV1AccountWithdrawResponse200")


@_attrs_define
class PostApiV1AccountWithdrawResponse200:
    """
    Attributes:
        transaction_id (str):
        amount (float):
        new_balance (float):
        created_at (str):
    """

    transaction_id: str
    amount: float
    new_balance: float
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        transaction_id = self.transaction_id

        amount = self.amount

        new_balance = self.new_balance

        created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "transactionId": transaction_id,
                "amount": amount,
                "newBalance": new_balance,
                "createdAt": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        transaction_id = d.pop("transactionId")

        amount = d.pop("amount")

        new_balance = d.pop("newBalance")

        created_at = d.pop("createdAt")

        post_api_v1_account_withdraw_response_200 = cls(
            transaction_id=transaction_id,
            amount=amount,
            new_balance=new_balance,
            created_at=created_at,
        )

        return post_api_v1_account_withdraw_response_200
