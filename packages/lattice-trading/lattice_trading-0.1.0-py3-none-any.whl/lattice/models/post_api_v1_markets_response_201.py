
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_api_v1_markets_response_201_outcomes_item import PostApiV1MarketsResponse201OutcomesItem


T = TypeVar("T", bound="PostApiV1MarketsResponse201")


@_attrs_define
class PostApiV1MarketsResponse201:
    """
    Attributes:
        id (str):
        title (str):
        status (str):
        outcomes (List['PostApiV1MarketsResponse201OutcomesItem']):
        created_at (str):
    """

    id: str
    title: str
    status: str
    outcomes: list["PostApiV1MarketsResponse201OutcomesItem"]
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        status = self.status

        outcomes = []
        for outcomes_item_data in self.outcomes:
            outcomes_item = outcomes_item_data.to_dict()
            outcomes.append(outcomes_item)

        created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "title": title,
                "status": status,
                "outcomes": outcomes,
                "createdAt": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.post_api_v1_markets_response_201_outcomes_item import PostApiV1MarketsResponse201OutcomesItem

        d = src_dict.copy()
        id = d.pop("id")

        title = d.pop("title")

        status = d.pop("status")

        outcomes = []
        _outcomes = d.pop("outcomes")
        for outcomes_item_data in _outcomes:
            outcomes_item = PostApiV1MarketsResponse201OutcomesItem.from_dict(outcomes_item_data)

            outcomes.append(outcomes_item)

        created_at = d.pop("createdAt")

        post_api_v1_markets_response_201 = cls(
            id=id,
            title=title,
            status=status,
            outcomes=outcomes,
            created_at=created_at,
        )

        return post_api_v1_markets_response_201
