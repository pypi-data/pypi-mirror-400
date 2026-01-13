
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostApiV1MarketsBodyOutcomesItemType3")


@_attrs_define
class PostApiV1MarketsBodyOutcomesItemType3:
    """
    Attributes:
        label (str):
        description (Union[Unset, str]):
    """

    label: str
    description: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "label": label,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        label = d.pop("label")

        description = d.pop("description", UNSET)

        post_api_v1_markets_body_outcomes_item_type_3 = cls(
            label=label,
            description=description,
        )

        return post_api_v1_markets_body_outcomes_item_type_3
