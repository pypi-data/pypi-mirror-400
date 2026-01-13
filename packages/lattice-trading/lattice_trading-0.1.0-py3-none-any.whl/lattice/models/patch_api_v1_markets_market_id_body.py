
from __future__ import annotations

import builtins
import datetime
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.patch_api_v1_markets_market_id_body_type import PatchApiV1MarketsMarketIdBodyType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.patch_api_v1_markets_market_id_body_metadata import PatchApiV1MarketsMarketIdBodyMetadata


T = TypeVar("T", bound="PatchApiV1MarketsMarketIdBody")


@_attrs_define
class PatchApiV1MarketsMarketIdBody:
    """
    Attributes:
        title (Union[Unset, str]):
        description (Union[Unset, str]):
        type (Union[Unset, PatchApiV1MarketsMarketIdBodyType]):
        close_time (Union[Unset, datetime.datetime]):
        trading_ends_at (Union[Unset, datetime.datetime]):
        metadata (Union[Unset, PatchApiV1MarketsMarketIdBodyMetadata]):
    """

    title: Unset | str = UNSET
    description: Unset | str = UNSET
    type: Unset | PatchApiV1MarketsMarketIdBodyType = UNSET
    close_time: Unset | datetime.datetime = UNSET
    trading_ends_at: Unset | datetime.datetime = UNSET
    metadata: Union[Unset, "PatchApiV1MarketsMarketIdBodyMetadata"] = UNSET

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        description = self.description

        type: Unset | str = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        close_time: Unset | str = UNSET
        if not isinstance(self.close_time, Unset):
            close_time = self.close_time.isoformat()

        trading_ends_at: Unset | str = UNSET
        if not isinstance(self.trading_ends_at, Unset):
            trading_ends_at = self.trading_ends_at.isoformat()

        metadata: Unset | dict[str, Any] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if description is not UNSET:
            field_dict["description"] = description
        if type is not UNSET:
            field_dict["type"] = type
        if close_time is not UNSET:
            field_dict["closeTime"] = close_time
        if trading_ends_at is not UNSET:
            field_dict["tradingEndsAt"] = trading_ends_at
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: builtins.type[T], src_dict: dict[str, Any]) -> T:
        from ..models.patch_api_v1_markets_market_id_body_metadata import PatchApiV1MarketsMarketIdBodyMetadata

        d = src_dict.copy()
        title = d.pop("title", UNSET)

        description = d.pop("description", UNSET)

        _type = d.pop("type", UNSET)
        type: Unset | PatchApiV1MarketsMarketIdBodyType
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = PatchApiV1MarketsMarketIdBodyType(_type)

        _close_time = d.pop("closeTime", UNSET)
        close_time: Unset | datetime.datetime
        if isinstance(_close_time, Unset):
            close_time = UNSET
        else:
            close_time = isoparse(_close_time)

        _trading_ends_at = d.pop("tradingEndsAt", UNSET)
        trading_ends_at: Unset | datetime.datetime
        if isinstance(_trading_ends_at, Unset):
            trading_ends_at = UNSET
        else:
            trading_ends_at = isoparse(_trading_ends_at)

        _metadata = d.pop("metadata", UNSET)
        metadata: Unset | PatchApiV1MarketsMarketIdBodyMetadata
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = PatchApiV1MarketsMarketIdBodyMetadata.from_dict(_metadata)

        patch_api_v1_markets_market_id_body = cls(
            title=title,
            description=description,
            type=type,
            close_time=close_time,
            trading_ends_at=trading_ends_at,
            metadata=metadata,
        )

        return patch_api_v1_markets_market_id_body
