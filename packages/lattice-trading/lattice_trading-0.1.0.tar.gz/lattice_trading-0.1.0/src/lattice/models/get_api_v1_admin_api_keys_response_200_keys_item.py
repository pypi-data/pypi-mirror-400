
from __future__ import annotations

from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.get_api_v1_admin_api_keys_response_200_keys_item_scopes_item import (
    GetApiV1AdminApiKeysResponse200KeysItemScopesItem,
)

T = TypeVar("T", bound="GetApiV1AdminApiKeysResponse200KeysItem")


@_attrs_define
class GetApiV1AdminApiKeysResponse200KeysItem:
    """
    Attributes:
        id (str):
        user_id (str):
        name (str):
        key_prefix (str):
        scopes (List[GetApiV1AdminApiKeysResponse200KeysItemScopesItem]):
        status (str):
        is_active (bool):
        expires_at (Union[None, str]):
        last_used_at (Union[None, str]):
        last_used_ip (Union[None, str]):
        rate_limit_override (Union[None, float]):
        ip_whitelist (Union[List[str], None]):
        created_at (str):
    """

    id: str
    user_id: str
    name: str
    key_prefix: str
    scopes: list[GetApiV1AdminApiKeysResponse200KeysItemScopesItem]
    status: str
    is_active: bool
    expires_at: None | str
    last_used_at: None | str
    last_used_ip: None | str
    rate_limit_override: None | float
    ip_whitelist: list[str] | None
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        user_id = self.user_id

        name = self.name

        key_prefix = self.key_prefix

        scopes = []
        for scopes_item_data in self.scopes:
            scopes_item = scopes_item_data.value
            scopes.append(scopes_item)

        status = self.status

        is_active = self.is_active

        expires_at: None | str
        expires_at = self.expires_at

        last_used_at: None | str
        last_used_at = self.last_used_at

        last_used_ip: None | str
        last_used_ip = self.last_used_ip

        rate_limit_override: None | float
        rate_limit_override = self.rate_limit_override

        ip_whitelist: list[str] | None
        if isinstance(self.ip_whitelist, list):
            ip_whitelist = self.ip_whitelist

        else:
            ip_whitelist = self.ip_whitelist

        created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "userId": user_id,
                "name": name,
                "keyPrefix": key_prefix,
                "scopes": scopes,
                "status": status,
                "isActive": is_active,
                "expiresAt": expires_at,
                "lastUsedAt": last_used_at,
                "lastUsedIp": last_used_ip,
                "rateLimitOverride": rate_limit_override,
                "ipWhitelist": ip_whitelist,
                "createdAt": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        user_id = d.pop("userId")

        name = d.pop("name")

        key_prefix = d.pop("keyPrefix")

        scopes = []
        _scopes = d.pop("scopes")
        for scopes_item_data in _scopes:
            scopes_item = GetApiV1AdminApiKeysResponse200KeysItemScopesItem(scopes_item_data)

            scopes.append(scopes_item)

        status = d.pop("status")

        is_active = d.pop("isActive")

        def _parse_expires_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        expires_at = _parse_expires_at(d.pop("expiresAt"))

        def _parse_last_used_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_used_at = _parse_last_used_at(d.pop("lastUsedAt"))

        def _parse_last_used_ip(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        last_used_ip = _parse_last_used_ip(d.pop("lastUsedIp"))

        def _parse_rate_limit_override(data: object) -> None | float:
            if data is None:
                return data
            return cast(None | float, data)

        rate_limit_override = _parse_rate_limit_override(d.pop("rateLimitOverride"))

        def _parse_ip_whitelist(data: object) -> list[str] | None:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                ip_whitelist_type_0 = cast(list[str], data)

                return ip_whitelist_type_0
            except:  # noqa: E722
                pass
            return cast(list[str] | None, data)

        ip_whitelist = _parse_ip_whitelist(d.pop("ipWhitelist"))

        created_at = d.pop("createdAt")

        get_api_v1_admin_api_keys_response_200_keys_item = cls(
            id=id,
            user_id=user_id,
            name=name,
            key_prefix=key_prefix,
            scopes=scopes,
            status=status,
            is_active=is_active,
            expires_at=expires_at,
            last_used_at=last_used_at,
            last_used_ip=last_used_ip,
            rate_limit_override=rate_limit_override,
            ip_whitelist=ip_whitelist,
            created_at=created_at,
        )

        return get_api_v1_admin_api_keys_response_200_keys_item
