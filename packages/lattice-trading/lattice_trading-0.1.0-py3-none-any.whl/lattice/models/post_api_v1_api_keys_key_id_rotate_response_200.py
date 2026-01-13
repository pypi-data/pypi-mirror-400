
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="PostApiV1ApiKeysKeyIdRotateResponse200")


@_attrs_define
class PostApiV1ApiKeysKeyIdRotateResponse200:
    """
    Attributes:
        key_id (str):
        key (str):
        message (str):
    """

    key_id: str
    key: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        key_id = self.key_id

        key = self.key

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "keyId": key_id,
                "key": key,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        key_id = d.pop("keyId")

        key = d.pop("key")

        message = d.pop("message")

        post_api_v1_api_keys_key_id_rotate_response_200 = cls(
            key_id=key_id,
            key=key,
            message=message,
        )

        return post_api_v1_api_keys_key_id_rotate_response_200
