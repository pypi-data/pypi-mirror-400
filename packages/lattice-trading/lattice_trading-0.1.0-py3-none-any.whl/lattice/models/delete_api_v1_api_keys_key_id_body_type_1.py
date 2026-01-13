
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeleteApiV1ApiKeysKeyIdBodyType1")


@_attrs_define
class DeleteApiV1ApiKeysKeyIdBodyType1:
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

        delete_api_v1_api_keys_key_id_body_type_1 = cls(
            reason=reason,
        )

        return delete_api_v1_api_keys_key_id_body_type_1
