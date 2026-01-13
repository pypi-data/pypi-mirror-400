
from __future__ import annotations

from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetApiV1TemplatesResponse200ItemVariablesItem")


@_attrs_define
class GetApiV1TemplatesResponse200ItemVariablesItem:
    """
    Attributes:
        key (str):
        label (str):
        type (str):
        required (bool):
        options (Union[Unset, List[str]]):
        placeholder (Union[Unset, str]):
    """

    key: str
    label: str
    type: str
    required: bool
    options: Unset | list[str] = UNSET
    placeholder: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        key = self.key

        label = self.label

        type = self.type

        required = self.required

        options: Unset | list[str] = UNSET
        if not isinstance(self.options, Unset):
            options = self.options

        placeholder = self.placeholder

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "key": key,
                "label": label,
                "type": type,
                "required": required,
            }
        )
        if options is not UNSET:
            field_dict["options"] = options
        if placeholder is not UNSET:
            field_dict["placeholder"] = placeholder

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        key = d.pop("key")

        label = d.pop("label")

        type = d.pop("type")

        required = d.pop("required")

        options = cast(list[str], d.pop("options", UNSET))

        placeholder = d.pop("placeholder", UNSET)

        get_api_v1_templates_response_200_item_variables_item = cls(
            key=key,
            label=label,
            type=type,
            required=required,
            options=options,
            placeholder=placeholder,
        )

        return get_api_v1_templates_response_200_item_variables_item
