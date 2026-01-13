
from __future__ import annotations

from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="PatchApiV1UsersUserIdResponse200")


@_attrs_define
class PatchApiV1UsersUserIdResponse200:
    """
    Attributes:
        id (str):
        display_name (Union[None, str]):
        updated_at (str):
    """

    id: str
    display_name: None | str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        display_name: None | str
        display_name = self.display_name

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "displayName": display_name,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        def _parse_display_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        display_name = _parse_display_name(d.pop("displayName"))

        updated_at = d.pop("updatedAt")

        patch_api_v1_users_user_id_response_200 = cls(
            id=id,
            display_name=display_name,
            updated_at=updated_at,
        )

        return patch_api_v1_users_user_id_response_200
