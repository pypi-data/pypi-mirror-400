
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostApiV1AccountWithdrawBody")


@_attrs_define
class PostApiV1AccountWithdrawBody:
    """
    Attributes:
        amount (int):
        reference (Union[Unset, str]):
    """

    amount: int
    reference: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        amount = self.amount

        reference = self.reference

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "amount": amount,
            }
        )
        if reference is not UNSET:
            field_dict["reference"] = reference

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        amount = d.pop("amount")

        reference = d.pop("reference", UNSET)

        post_api_v1_account_withdraw_body = cls(
            amount=amount,
            reference=reference,
        )

        return post_api_v1_account_withdraw_body
