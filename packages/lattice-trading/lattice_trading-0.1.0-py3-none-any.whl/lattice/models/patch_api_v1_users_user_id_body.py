
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.patch_api_v1_users_user_id_body_metadata import PatchApiV1UsersUserIdBodyMetadata


T = TypeVar("T", bound="PatchApiV1UsersUserIdBody")


@_attrs_define
class PatchApiV1UsersUserIdBody:
    """
    Attributes:
        display_name (Union[Unset, str]):
        metadata (Union[Unset, PatchApiV1UsersUserIdBodyMetadata]):
    """

    display_name: Unset | str = UNSET
    metadata: Union[Unset, "PatchApiV1UsersUserIdBodyMetadata"] = UNSET

    def to_dict(self) -> dict[str, Any]:
        display_name = self.display_name

        metadata: Unset | dict[str, Any] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update({})
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.patch_api_v1_users_user_id_body_metadata import PatchApiV1UsersUserIdBodyMetadata

        d = src_dict.copy()
        display_name = d.pop("displayName", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Unset | PatchApiV1UsersUserIdBodyMetadata
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = PatchApiV1UsersUserIdBodyMetadata.from_dict(_metadata)

        patch_api_v1_users_user_id_body = cls(
            display_name=display_name,
            metadata=metadata,
        )

        return patch_api_v1_users_user_id_body
