
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.post_api_v1_templates_id_apply_body_variables import PostApiV1TemplatesIdApplyBodyVariables


T = TypeVar("T", bound="PostApiV1TemplatesIdApplyBody")


@_attrs_define
class PostApiV1TemplatesIdApplyBody:
    """
    Attributes:
        variables (PostApiV1TemplatesIdApplyBodyVariables):
    """

    variables: "PostApiV1TemplatesIdApplyBodyVariables"

    def to_dict(self) -> dict[str, Any]:
        variables = self.variables.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "variables": variables,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.post_api_v1_templates_id_apply_body_variables import PostApiV1TemplatesIdApplyBodyVariables

        d = src_dict.copy()
        variables = PostApiV1TemplatesIdApplyBodyVariables.from_dict(d.pop("variables"))

        post_api_v1_templates_id_apply_body = cls(
            variables=variables,
        )

        return post_api_v1_templates_id_apply_body
