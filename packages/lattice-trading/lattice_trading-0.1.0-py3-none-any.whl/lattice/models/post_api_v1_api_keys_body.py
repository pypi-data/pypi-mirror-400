
from __future__ import annotations

import datetime
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.post_api_v1_api_keys_body_scopes_item import PostApiV1ApiKeysBodyScopesItem
from ..types import UNSET, Unset

T = TypeVar("T", bound="PostApiV1ApiKeysBody")


@_attrs_define
class PostApiV1ApiKeysBody:
    """
    Attributes:
        name (str):
        scopes (List[PostApiV1ApiKeysBodyScopesItem]):
        expires_at (Union[Unset, datetime.datetime]):
        ip_whitelist (Union[Unset, List[str]]):
        rate_limit_override (Union[Unset, int]):
    """

    name: str
    scopes: list[PostApiV1ApiKeysBodyScopesItem]
    expires_at: Unset | datetime.datetime = UNSET
    ip_whitelist: Unset | list[str] = UNSET
    rate_limit_override: Unset | int = UNSET

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        scopes = []
        for scopes_item_data in self.scopes:
            scopes_item = scopes_item_data.value
            scopes.append(scopes_item)

        expires_at: Unset | str = UNSET
        if not isinstance(self.expires_at, Unset):
            expires_at = self.expires_at.isoformat()

        ip_whitelist: Unset | list[str] = UNSET
        if not isinstance(self.ip_whitelist, Unset):
            ip_whitelist = self.ip_whitelist

        rate_limit_override = self.rate_limit_override

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "scopes": scopes,
            }
        )
        if expires_at is not UNSET:
            field_dict["expiresAt"] = expires_at
        if ip_whitelist is not UNSET:
            field_dict["ipWhitelist"] = ip_whitelist
        if rate_limit_override is not UNSET:
            field_dict["rateLimitOverride"] = rate_limit_override

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        scopes = []
        _scopes = d.pop("scopes")
        for scopes_item_data in _scopes:
            scopes_item = PostApiV1ApiKeysBodyScopesItem(scopes_item_data)

            scopes.append(scopes_item)

        _expires_at = d.pop("expiresAt", UNSET)
        expires_at: Unset | datetime.datetime
        if isinstance(_expires_at, Unset):
            expires_at = UNSET
        else:
            expires_at = isoparse(_expires_at)

        ip_whitelist = cast(list[str], d.pop("ipWhitelist", UNSET))

        rate_limit_override = d.pop("rateLimitOverride", UNSET)

        post_api_v1_api_keys_body = cls(
            name=name,
            scopes=scopes,
            expires_at=expires_at,
            ip_whitelist=ip_whitelist,
            rate_limit_override=rate_limit_override,
        )

        return post_api_v1_api_keys_body
