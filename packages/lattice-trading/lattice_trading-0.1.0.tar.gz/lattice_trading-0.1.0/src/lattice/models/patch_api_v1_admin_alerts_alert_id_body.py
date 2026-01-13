
from __future__ import annotations

from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.patch_api_v1_admin_alerts_alert_id_body_status import PatchApiV1AdminAlertsAlertIdBodyStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="PatchApiV1AdminAlertsAlertIdBody")


@_attrs_define
class PatchApiV1AdminAlertsAlertIdBody:
    """
    Attributes:
        status (PatchApiV1AdminAlertsAlertIdBodyStatus):
        notes (Union[Unset, str]):
    """

    status: PatchApiV1AdminAlertsAlertIdBodyStatus
    notes: Unset | str = UNSET

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        notes = self.notes

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "status": status,
            }
        )
        if notes is not UNSET:
            field_dict["notes"] = notes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        status = PatchApiV1AdminAlertsAlertIdBodyStatus(d.pop("status"))

        notes = d.pop("notes", UNSET)

        patch_api_v1_admin_alerts_alert_id_body = cls(
            status=status,
            notes=notes,
        )

        return patch_api_v1_admin_alerts_alert_id_body
