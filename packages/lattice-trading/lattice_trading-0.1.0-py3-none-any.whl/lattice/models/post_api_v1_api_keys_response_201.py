
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.post_api_v1_api_keys_response_201_scopes_item import PostApiV1ApiKeysResponse201ScopesItem

T = TypeVar("T", bound="PostApiV1ApiKeysResponse201")


@_attrs_define
class PostApiV1ApiKeysResponse201:
    """
    Attributes:
        key_id (str):
        key (str):
        name (str):
        scopes (List[PostApiV1ApiKeysResponse201ScopesItem]):
        message (str):
    """

    key_id: str
    key: str
    name: str
    scopes: list[PostApiV1ApiKeysResponse201ScopesItem]
    message: str

    def to_dict(self) -> dict[str, Any]:
        key_id = self.key_id

        key = self.key

        name = self.name

        scopes = []
        for scopes_item_data in self.scopes:
            scopes_item = scopes_item_data.value
            scopes.append(scopes_item)

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "keyId": key_id,
                "key": key,
                "name": name,
                "scopes": scopes,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        key_id = d.pop("keyId")

        key = d.pop("key")

        name = d.pop("name")

        scopes = []
        _scopes = d.pop("scopes")
        for scopes_item_data in _scopes:
            scopes_item = PostApiV1ApiKeysResponse201ScopesItem(scopes_item_data)

            scopes.append(scopes_item)

        message = d.pop("message")

        post_api_v1_api_keys_response_201 = cls(
            key_id=key_id,
            key=key,
            name=name,
            scopes=scopes,
            message=message,
        )

        return post_api_v1_api_keys_response_201
