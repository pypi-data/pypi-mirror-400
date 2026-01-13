
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_api_v1_account_transactions_response_200_transactions_item import (
        GetApiV1AccountTransactionsResponse200TransactionsItem,
    )


T = TypeVar("T", bound="GetApiV1AccountTransactionsResponse200")


@_attrs_define
class GetApiV1AccountTransactionsResponse200:
    """
    Attributes:
        transactions (List['GetApiV1AccountTransactionsResponse200TransactionsItem']):
        total (float):
        limit (float):
        offset (float):
        has_more (bool):
        next_cursor (Union[Unset, str]):
    """

    transactions: list["GetApiV1AccountTransactionsResponse200TransactionsItem"]
    total: float
    limit: float
    offset: float
    has_more: bool
    next_cursor: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        transactions = []
        for transactions_item_data in self.transactions:
            transactions_item = transactions_item_data.to_dict()
            transactions.append(transactions_item)

        total = self.total

        limit = self.limit

        offset = self.offset

        has_more = self.has_more

        next_cursor = self.next_cursor

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "transactions": transactions,
                "total": total,
                "limit": limit,
                "offset": offset,
                "hasMore": has_more,
            }
        )
        if next_cursor is not UNSET:
            field_dict["nextCursor"] = next_cursor

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_account_transactions_response_200_transactions_item import (
            GetApiV1AccountTransactionsResponse200TransactionsItem,
        )

        d = src_dict.copy()
        transactions = []
        _transactions = d.pop("transactions")
        for transactions_item_data in _transactions:
            transactions_item = GetApiV1AccountTransactionsResponse200TransactionsItem.from_dict(transactions_item_data)

            transactions.append(transactions_item)

        total = d.pop("total")

        limit = d.pop("limit")

        offset = d.pop("offset")

        has_more = d.pop("hasMore")

        next_cursor = d.pop("nextCursor", UNSET)

        get_api_v1_account_transactions_response_200 = cls(
            transactions=transactions,
            total=total,
            limit=limit,
            offset=offset,
            has_more=has_more,
            next_cursor=next_cursor,
        )

        return get_api_v1_account_transactions_response_200
