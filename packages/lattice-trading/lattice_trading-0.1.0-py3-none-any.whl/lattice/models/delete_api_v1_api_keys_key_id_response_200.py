
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="DeleteApiV1ApiKeysKeyIdResponse200")


@_attrs_define
class DeleteApiV1ApiKeysKeyIdResponse200:
    """
    Attributes:
        success (bool):
        message (str):
    """

    success: bool
    message: str

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "success": success,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        success = d.pop("success")

        message = d.pop("message")

        delete_api_v1_api_keys_key_id_response_200 = cls(
            success=success,
            message=message,
        )

        return delete_api_v1_api_keys_key_id_response_200
