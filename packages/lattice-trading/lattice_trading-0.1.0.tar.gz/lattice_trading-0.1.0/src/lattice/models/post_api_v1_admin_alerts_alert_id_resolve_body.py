
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.post_api_v1_admin_alerts_alert_id_resolve_body_resolution import (
    PostApiV1AdminAlertsAlertIdResolveBodyResolution,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="PostApiV1AdminAlertsAlertIdResolveBody")


@_attrs_define
class PostApiV1AdminAlertsAlertIdResolveBody:
    """
    Attributes:
        resolution (PostApiV1AdminAlertsAlertIdResolveBodyResolution):
        notes (str):
        assignee (Union[Unset, str]):
    """

    resolution: PostApiV1AdminAlertsAlertIdResolveBodyResolution
    notes: str
    assignee: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        resolution = self.resolution.value

        notes = self.notes

        assignee = self.assignee

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "resolution": resolution,
                "notes": notes,
            }
        )
        if assignee is not UNSET:
            field_dict["assignee"] = assignee

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        resolution = PostApiV1AdminAlertsAlertIdResolveBodyResolution(d.pop("resolution"))

        notes = d.pop("notes")

        assignee = d.pop("assignee", UNSET)

        post_api_v1_admin_alerts_alert_id_resolve_body = cls(
            resolution=resolution,
            notes=notes,
            assignee=assignee,
        )

        return post_api_v1_admin_alerts_alert_id_resolve_body
