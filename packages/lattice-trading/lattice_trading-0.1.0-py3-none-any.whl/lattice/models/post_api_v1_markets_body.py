
from __future__ import annotations

import builtins
import datetime
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.post_api_v1_markets_body_type import PostApiV1MarketsBodyType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_api_v1_markets_body_metadata import PostApiV1MarketsBodyMetadata
    from ..models.post_api_v1_markets_body_outcomes_item_type_1 import PostApiV1MarketsBodyOutcomesItemType1
    from ..models.post_api_v1_markets_body_outcomes_item_type_2 import PostApiV1MarketsBodyOutcomesItemType2
    from ..models.post_api_v1_markets_body_outcomes_item_type_3 import PostApiV1MarketsBodyOutcomesItemType3


T = TypeVar("T", bound="PostApiV1MarketsBody")


@_attrs_define
class PostApiV1MarketsBody:
    """
    Attributes:
        title (str):
        outcomes (List[Union['PostApiV1MarketsBodyOutcomesItemType1', 'PostApiV1MarketsBodyOutcomesItemType2',
            'PostApiV1MarketsBodyOutcomesItemType3', str]]):
        description (Union[Unset, str]):
        type (Union[Unset, PostApiV1MarketsBodyType]):
        close_time (Union[Unset, datetime.datetime]):
        trading_ends_at (Union[Unset, datetime.datetime]):
        metadata (Union[Unset, PostApiV1MarketsBodyMetadata]):
    """

    title: str
    outcomes: list[
        Union[
            "PostApiV1MarketsBodyOutcomesItemType1",
            "PostApiV1MarketsBodyOutcomesItemType2",
            "PostApiV1MarketsBodyOutcomesItemType3",
            str,
        ]
    ]
    description: Unset | str = UNSET
    type: Unset | PostApiV1MarketsBodyType = UNSET
    close_time: Unset | datetime.datetime = UNSET
    trading_ends_at: Unset | datetime.datetime = UNSET
    metadata: Union[Unset, "PostApiV1MarketsBodyMetadata"] = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.post_api_v1_markets_body_outcomes_item_type_1 import PostApiV1MarketsBodyOutcomesItemType1
        from ..models.post_api_v1_markets_body_outcomes_item_type_2 import PostApiV1MarketsBodyOutcomesItemType2
        from ..models.post_api_v1_markets_body_outcomes_item_type_3 import PostApiV1MarketsBodyOutcomesItemType3

        title = self.title

        outcomes = []
        for outcomes_item_data in self.outcomes:
            outcomes_item: dict[str, Any] | str
            if isinstance(outcomes_item_data, PostApiV1MarketsBodyOutcomesItemType1):
                outcomes_item = outcomes_item_data.to_dict()
            elif isinstance(outcomes_item_data, PostApiV1MarketsBodyOutcomesItemType2):
                outcomes_item = outcomes_item_data.to_dict()
            elif isinstance(outcomes_item_data, PostApiV1MarketsBodyOutcomesItemType3):
                outcomes_item = outcomes_item_data.to_dict()
            else:
                outcomes_item = outcomes_item_data
            outcomes.append(outcomes_item)

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
        field_dict.update(
            {
                "title": title,
                "outcomes": outcomes,
            }
        )
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
        from ..models.post_api_v1_markets_body_metadata import PostApiV1MarketsBodyMetadata
        from ..models.post_api_v1_markets_body_outcomes_item_type_1 import PostApiV1MarketsBodyOutcomesItemType1
        from ..models.post_api_v1_markets_body_outcomes_item_type_2 import PostApiV1MarketsBodyOutcomesItemType2
        from ..models.post_api_v1_markets_body_outcomes_item_type_3 import PostApiV1MarketsBodyOutcomesItemType3

        d = src_dict.copy()
        title = d.pop("title")

        outcomes = []
        _outcomes = d.pop("outcomes")
        for outcomes_item_data in _outcomes:

            def _parse_outcomes_item(
                data: object,
            ) -> Union[
                "PostApiV1MarketsBodyOutcomesItemType1",
                "PostApiV1MarketsBodyOutcomesItemType2",
                "PostApiV1MarketsBodyOutcomesItemType3",
                str,
            ]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    outcomes_item_type_1 = PostApiV1MarketsBodyOutcomesItemType1.from_dict(data)

                    return outcomes_item_type_1
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    outcomes_item_type_2 = PostApiV1MarketsBodyOutcomesItemType2.from_dict(data)

                    return outcomes_item_type_2
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    outcomes_item_type_3 = PostApiV1MarketsBodyOutcomesItemType3.from_dict(data)

                    return outcomes_item_type_3
                except:  # noqa: E722
                    pass
                return cast(
                    Union[
                        "PostApiV1MarketsBodyOutcomesItemType1",
                        "PostApiV1MarketsBodyOutcomesItemType2",
                        "PostApiV1MarketsBodyOutcomesItemType3",
                        str,
                    ],
                    data,
                )

            outcomes_item = _parse_outcomes_item(outcomes_item_data)

            outcomes.append(outcomes_item)

        description = d.pop("description", UNSET)

        _type = d.pop("type", UNSET)
        type: Unset | PostApiV1MarketsBodyType
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = PostApiV1MarketsBodyType(_type)

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
        metadata: Unset | PostApiV1MarketsBodyMetadata
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = PostApiV1MarketsBodyMetadata.from_dict(_metadata)

        post_api_v1_markets_body = cls(
            title=title,
            outcomes=outcomes,
            description=description,
            type=type,
            close_time=close_time,
            trading_ends_at=trading_ends_at,
            metadata=metadata,
        )

        return post_api_v1_markets_body
