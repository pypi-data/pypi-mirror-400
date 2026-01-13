
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostApiV1ApiKeysKeyIdRotateBody")


@_attrs_define
class PostApiV1ApiKeysKeyIdRotateBody:
    """
    Attributes:
        grace_period_hours (Union[Unset, float]):  Default: 24.0.
    """

    grace_period_hours: Unset | float = 24.0

    def to_dict(self) -> dict[str, Any]:
        grace_period_hours = self.grace_period_hours

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if grace_period_hours is not UNSET:
            field_dict["gracePeriodHours"] = grace_period_hours

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        grace_period_hours = d.pop("gracePeriodHours", UNSET)

        post_api_v1_api_keys_key_id_rotate_body = cls(
            grace_period_hours=grace_period_hours,
        )

        return post_api_v1_api_keys_key_id_rotate_body
