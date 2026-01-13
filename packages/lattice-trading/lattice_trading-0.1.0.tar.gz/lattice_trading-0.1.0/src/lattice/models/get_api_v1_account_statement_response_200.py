
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_account_statement_response_200_period import GetApiV1AccountStatementResponse200Period
    from ..models.get_api_v1_account_statement_response_200_transactions_item import (
        GetApiV1AccountStatementResponse200TransactionsItem,
    )


T = TypeVar("T", bound="GetApiV1AccountStatementResponse200")


@_attrs_define
class GetApiV1AccountStatementResponse200:
    """
    Attributes:
        account_id (str):
        opening_balance (float):
        closing_balance (float):
        period (GetApiV1AccountStatementResponse200Period):
        transactions (List['GetApiV1AccountStatementResponse200TransactionsItem']):
    """

    account_id: str
    opening_balance: float
    closing_balance: float
    period: "GetApiV1AccountStatementResponse200Period"
    transactions: list["GetApiV1AccountStatementResponse200TransactionsItem"]

    def to_dict(self) -> dict[str, Any]:
        account_id = self.account_id

        opening_balance = self.opening_balance

        closing_balance = self.closing_balance

        period = self.period.to_dict()

        transactions = []
        for transactions_item_data in self.transactions:
            transactions_item = transactions_item_data.to_dict()
            transactions.append(transactions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "accountId": account_id,
                "openingBalance": opening_balance,
                "closingBalance": closing_balance,
                "period": period,
                "transactions": transactions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_account_statement_response_200_period import GetApiV1AccountStatementResponse200Period
        from ..models.get_api_v1_account_statement_response_200_transactions_item import (
            GetApiV1AccountStatementResponse200TransactionsItem,
        )

        d = src_dict.copy()
        account_id = d.pop("accountId")

        opening_balance = d.pop("openingBalance")

        closing_balance = d.pop("closingBalance")

        period = GetApiV1AccountStatementResponse200Period.from_dict(d.pop("period"))

        transactions = []
        _transactions = d.pop("transactions")
        for transactions_item_data in _transactions:
            transactions_item = GetApiV1AccountStatementResponse200TransactionsItem.from_dict(transactions_item_data)

            transactions.append(transactions_item)

        get_api_v1_account_statement_response_200 = cls(
            account_id=account_id,
            opening_balance=opening_balance,
            closing_balance=closing_balance,
            period=period,
            transactions=transactions,
        )

        return get_api_v1_account_statement_response_200
