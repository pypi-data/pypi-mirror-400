
from __future__ import annotations

from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="PostApiV1TemplatesIdApplyResponse400")


@_attrs_define
class PostApiV1TemplatesIdApplyResponse400:
    """
    Attributes:
        error (str):
        code (str):
        missing (Union[Unset, List[str]]):
    """

    error: str
    code: str
    missing: Unset | list[str] = UNSET

    def to_dict(self) -> dict[str, Any]:
        error = self.error

        code = self.code

        missing: Unset | list[str] = UNSET
        if not isinstance(self.missing, Unset):
            missing = self.missing

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "error": error,
                "code": code,
            }
        )
        if missing is not UNSET:
            field_dict["missing"] = missing

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        error = d.pop("error")

        code = d.pop("code")

        missing = cast(list[str], d.pop("missing", UNSET))

        post_api_v1_templates_id_apply_response_400 = cls(
            error=error,
            code=code,
            missing=missing,
        )

        return post_api_v1_templates_id_apply_response_400
