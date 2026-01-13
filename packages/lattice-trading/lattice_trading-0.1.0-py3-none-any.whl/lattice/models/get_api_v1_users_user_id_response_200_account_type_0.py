
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1UsersUserIdResponse200AccountType0")


@_attrs_define
class GetApiV1UsersUserIdResponse200AccountType0:
    """
    Attributes:
        id (str):
        balance (float):
        hold_balance (float):
        currency (str):
    """

    id: str
    balance: float
    hold_balance: float
    currency: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        balance = self.balance

        hold_balance = self.hold_balance

        currency = self.currency

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "balance": balance,
                "holdBalance": hold_balance,
                "currency": currency,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        balance = d.pop("balance")

        hold_balance = d.pop("holdBalance")

        currency = d.pop("currency")

        get_api_v1_users_user_id_response_200_account_type_0 = cls(
            id=id,
            balance=balance,
            hold_balance=hold_balance,
            currency=currency,
        )

        return get_api_v1_users_user_id_response_200_account_type_0
