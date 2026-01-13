
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_api_v1_users_body_metadata import PostApiV1UsersBodyMetadata


T = TypeVar("T", bound="PostApiV1UsersBody")


@_attrs_define
class PostApiV1UsersBody:
    """
    Attributes:
        email (str):
        external_id (Union[Unset, str]):
        display_name (Union[Unset, str]):
        metadata (Union[Unset, PostApiV1UsersBodyMetadata]):
    """

    email: str
    external_id: Unset | str = UNSET
    display_name: Unset | str = UNSET
    metadata: Union[Unset, "PostApiV1UsersBodyMetadata"] = UNSET

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        external_id = self.external_id

        display_name = self.display_name

        metadata: Unset | dict[str, Any] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "email": email,
            }
        )
        if external_id is not UNSET:
            field_dict["externalId"] = external_id
        if display_name is not UNSET:
            field_dict["displayName"] = display_name
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.post_api_v1_users_body_metadata import PostApiV1UsersBodyMetadata

        d = src_dict.copy()
        email = d.pop("email")

        external_id = d.pop("externalId", UNSET)

        display_name = d.pop("displayName", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Unset | PostApiV1UsersBodyMetadata
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = PostApiV1UsersBodyMetadata.from_dict(_metadata)

        post_api_v1_users_body = cls(
            email=email,
            external_id=external_id,
            display_name=display_name,
            metadata=metadata,
        )

        return post_api_v1_users_body
