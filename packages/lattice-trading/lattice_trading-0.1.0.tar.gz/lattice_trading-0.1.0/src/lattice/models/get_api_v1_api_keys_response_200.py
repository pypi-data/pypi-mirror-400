
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_api_keys_response_200_keys_item import GetApiV1ApiKeysResponse200KeysItem


T = TypeVar("T", bound="GetApiV1ApiKeysResponse200")


@_attrs_define
class GetApiV1ApiKeysResponse200:
    """
    Attributes:
        keys (List['GetApiV1ApiKeysResponse200KeysItem']):
    """

    keys: list["GetApiV1ApiKeysResponse200KeysItem"]

    def to_dict(self) -> dict[str, Any]:
        keys = []
        for keys_item_data in self.keys:
            keys_item = keys_item_data.to_dict()
            keys.append(keys_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "keys": keys,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_api_keys_response_200_keys_item import GetApiV1ApiKeysResponse200KeysItem

        d = src_dict.copy()
        keys = []
        _keys = d.pop("keys")
        for keys_item_data in _keys:
            keys_item = GetApiV1ApiKeysResponse200KeysItem.from_dict(keys_item_data)

            keys.append(keys_item)

        get_api_v1_api_keys_response_200 = cls(
            keys=keys,
        )

        return get_api_v1_api_keys_response_200
