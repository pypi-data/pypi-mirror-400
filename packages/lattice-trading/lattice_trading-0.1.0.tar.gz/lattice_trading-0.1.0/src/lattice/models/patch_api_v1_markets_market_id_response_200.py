
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PatchApiV1MarketsMarketIdResponse200")


@_attrs_define
class PatchApiV1MarketsMarketIdResponse200:
    """
    Attributes:
        id (str):
        title (str):
        status (str):
        updated_at (str):
    """

    id: str
    title: str
    status: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        status = self.status

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "title": title,
                "status": status,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        title = d.pop("title")

        status = d.pop("status")

        updated_at = d.pop("updatedAt")

        patch_api_v1_markets_market_id_response_200 = cls(
            id=id,
            title=title,
            status=status,
            updated_at=updated_at,
        )

        return patch_api_v1_markets_market_id_response_200
