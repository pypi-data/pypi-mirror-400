
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostApiV1MarketsResponse201OutcomesItem")


@_attrs_define
class PostApiV1MarketsResponse201OutcomesItem:
    """
    Attributes:
        id (str):
        name (str):
    """

    id: str
    name: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        post_api_v1_markets_response_201_outcomes_item = cls(
            id=id,
            name=name,
        )

        return post_api_v1_markets_response_201_outcomes_item
