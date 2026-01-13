
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1AccountResponse200")


@_attrs_define
class GetApiV1AccountResponse200:
    """
    Attributes:
        id (str):
        currency (str):
        balance (float):
        available_balance (float):
        hold_balance (float):
        created_at (str):
        updated_at (str):
    """

    id: str
    currency: str
    balance: float
    available_balance: float
    hold_balance: float
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        currency = self.currency

        balance = self.balance

        available_balance = self.available_balance

        hold_balance = self.hold_balance

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "currency": currency,
                "balance": balance,
                "availableBalance": available_balance,
                "holdBalance": hold_balance,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        currency = d.pop("currency")

        balance = d.pop("balance")

        available_balance = d.pop("availableBalance")

        hold_balance = d.pop("holdBalance")

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        get_api_v1_account_response_200 = cls(
            id=id,
            currency=currency,
            balance=balance,
            available_balance=available_balance,
            hold_balance=hold_balance,
            created_at=created_at,
            updated_at=updated_at,
        )

        return get_api_v1_account_response_200
