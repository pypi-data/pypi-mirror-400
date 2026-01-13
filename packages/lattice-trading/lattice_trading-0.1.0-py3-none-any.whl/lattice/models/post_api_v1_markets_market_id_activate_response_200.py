
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostApiV1MarketsMarketIdActivateResponse200")


@_attrs_define
class PostApiV1MarketsMarketIdActivateResponse200:
    """
    Attributes:
        id (str):
        status (str):
        published_at (str):
    """

    id: str
    status: str
    published_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        status = self.status

        published_at = self.published_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "status": status,
                "publishedAt": published_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        status = d.pop("status")

        published_at = d.pop("publishedAt")

        post_api_v1_markets_market_id_activate_response_200 = cls(
            id=id,
            status=status,
            published_at=published_at,
        )

        return post_api_v1_markets_market_id_activate_response_200
