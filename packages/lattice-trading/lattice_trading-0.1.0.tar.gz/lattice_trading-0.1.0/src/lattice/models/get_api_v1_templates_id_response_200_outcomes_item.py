
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="GetApiV1TemplatesIdResponse200OutcomesItem")


@_attrs_define
class GetApiV1TemplatesIdResponse200OutcomesItem:
    """
    Attributes:
        name_template (str):
        default_probability (float):
    """

    name_template: str
    default_probability: float

    def to_dict(self) -> dict[str, Any]:
        name_template = self.name_template

        default_probability = self.default_probability

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "nameTemplate": name_template,
                "defaultProbability": default_probability,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        name_template = d.pop("nameTemplate")

        default_probability = d.pop("defaultProbability")

        get_api_v1_templates_id_response_200_outcomes_item = cls(
            name_template=name_template,
            default_probability=default_probability,
        )

        return get_api_v1_templates_id_response_200_outcomes_item
