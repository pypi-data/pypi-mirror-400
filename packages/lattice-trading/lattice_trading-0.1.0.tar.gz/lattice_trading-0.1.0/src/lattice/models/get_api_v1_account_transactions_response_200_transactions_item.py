
from __future__ import annotations

from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetApiV1AccountTransactionsResponse200TransactionsItem")


@_attrs_define
class GetApiV1AccountTransactionsResponse200TransactionsItem:
    """
    Attributes:
        id (str):
        type (str):
        amount (float):
        hold_amount (float):
        balance_after (float):
        hold_balance_after (float):
        running_balance (float):
        created_at (str):
        reference_type (Union[None, Unset, str]):
        reference_id (Union[None, Unset, str]):
        description (Union[None, Unset, str]):
    """

    id: str
    type: str
    amount: float
    hold_amount: float
    balance_after: float
    hold_balance_after: float
    running_balance: float
    created_at: str
    reference_type: None | Unset | str = UNSET
    reference_id: None | Unset | str = UNSET
    description: None | Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type = self.type

        amount = self.amount

        hold_amount = self.hold_amount

        balance_after = self.balance_after

        hold_balance_after = self.hold_balance_after

        running_balance = self.running_balance

        created_at = self.created_at

        reference_type: None | Unset | str
        if isinstance(self.reference_type, Unset):
            reference_type = UNSET
        else:
            reference_type = self.reference_type

        reference_id: None | Unset | str
        if isinstance(self.reference_id, Unset):
            reference_id = UNSET
        else:
            reference_id = self.reference_id

        description: None | Unset | str
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "type": type,
                "amount": amount,
                "holdAmount": hold_amount,
                "balanceAfter": balance_after,
                "holdBalanceAfter": hold_balance_after,
                "runningBalance": running_balance,
                "createdAt": created_at,
            }
        )
        if reference_type is not UNSET:
            field_dict["referenceType"] = reference_type
        if reference_id is not UNSET:
            field_dict["referenceId"] = reference_id
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        type = d.pop("type")

        amount = d.pop("amount")

        hold_amount = d.pop("holdAmount")

        balance_after = d.pop("balanceAfter")

        hold_balance_after = d.pop("holdBalanceAfter")

        running_balance = d.pop("runningBalance")

        created_at = d.pop("createdAt")

        def _parse_reference_type(data: object) -> None | Unset | str:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | Unset | str, data)

        reference_type = _parse_reference_type(d.pop("referenceType", UNSET))

        def _parse_reference_id(data: object) -> None | Unset | str:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | Unset | str, data)

        reference_id = _parse_reference_id(d.pop("referenceId", UNSET))

        def _parse_description(data: object) -> None | Unset | str:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | Unset | str, data)

        description = _parse_description(d.pop("description", UNSET))

        get_api_v1_account_transactions_response_200_transactions_item = cls(
            id=id,
            type=type,
            amount=amount,
            hold_amount=hold_amount,
            balance_after=balance_after,
            hold_balance_after=hold_balance_after,
            running_balance=running_balance,
            created_at=created_at,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description,
        )

        return get_api_v1_account_transactions_response_200_transactions_item
