
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostApiV1AdminMarketsMarketIdVoidBody")


@_attrs_define
class PostApiV1AdminMarketsMarketIdVoidBody:
    """
    Attributes:
        reason (Union[Unset, str]):
    """

    reason: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        reason = self.reason

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if reason is not UNSET:
            field_dict["reason"] = reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        reason = d.pop("reason", UNSET)

        post_api_v1_admin_markets_market_id_void_body = cls(
            reason=reason,
        )

        return post_api_v1_admin_markets_market_id_void_body
