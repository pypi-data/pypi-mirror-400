
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostApiV1MarketsBodyOutcomesItemType2")


@_attrs_define
class PostApiV1MarketsBodyOutcomesItemType2:
    """
    Attributes:
        title (str):
        description (Union[Unset, str]):
    """

    title: str
    description: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "title": title,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        title = d.pop("title")

        description = d.pop("description", UNSET)

        post_api_v1_markets_body_outcomes_item_type_2 = cls(
            title=title,
            description=description,
        )

        return post_api_v1_markets_body_outcomes_item_type_2
