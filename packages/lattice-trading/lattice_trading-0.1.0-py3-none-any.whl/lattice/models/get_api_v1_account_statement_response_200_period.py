
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1AccountStatementResponse200Period")


@_attrs_define
class GetApiV1AccountStatementResponse200Period:
    """
    Attributes:
        start_date (str):
        end_date (str):
    """

    start_date: str
    end_date: str

    def to_dict(self) -> dict[str, Any]:
        start_date = self.start_date

        end_date = self.end_date

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "startDate": start_date,
                "endDate": end_date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        start_date = d.pop("startDate")

        end_date = d.pop("endDate")

        get_api_v1_account_statement_response_200_period = cls(
            start_date=start_date,
            end_date=end_date,
        )

        return get_api_v1_account_statement_response_200_period
