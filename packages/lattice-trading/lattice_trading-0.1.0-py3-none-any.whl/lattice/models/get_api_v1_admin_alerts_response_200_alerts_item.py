
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_admin_alerts_response_200_alerts_item_evidence_type_0 import (
        GetApiV1AdminAlertsResponse200AlertsItemEvidenceType0,
    )


T = TypeVar("T", bound="GetApiV1AdminAlertsResponse200AlertsItem")


@_attrs_define
class GetApiV1AdminAlertsResponse200AlertsItem:
    """
    Attributes:
        id (str):
        alert_type (str):
        severity (str):
        status (str):
        subject_type (str):
        subject_id (str):
        title (str):
        description (Union[None, str]):
        evidence (Union['GetApiV1AdminAlertsResponse200AlertsItemEvidenceType0', None]):
        resolved_at (Union[None, str]):
        resolved_by (Union[None, str]):
        resolution (Union[None, str]):
        created_at (str):
        updated_at (str):
    """

    id: str
    alert_type: str
    severity: str
    status: str
    subject_type: str
    subject_id: str
    title: str
    description: None | str
    evidence: Union["GetApiV1AdminAlertsResponse200AlertsItemEvidenceType0", None]
    resolved_at: None | str
    resolved_by: None | str
    resolution: None | str
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_api_v1_admin_alerts_response_200_alerts_item_evidence_type_0 import (
            GetApiV1AdminAlertsResponse200AlertsItemEvidenceType0,
        )

        id = self.id

        alert_type = self.alert_type

        severity = self.severity

        status = self.status

        subject_type = self.subject_type

        subject_id = self.subject_id

        title = self.title

        description: None | str
        description = self.description

        evidence: dict[str, Any] | None
        if isinstance(self.evidence, GetApiV1AdminAlertsResponse200AlertsItemEvidenceType0):
            evidence = self.evidence.to_dict()
        else:
            evidence = self.evidence

        resolved_at: None | str
        resolved_at = self.resolved_at

        resolved_by: None | str
        resolved_by = self.resolved_by

        resolution: None | str
        resolution = self.resolution

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "alertType": alert_type,
                "severity": severity,
                "status": status,
                "subjectType": subject_type,
                "subjectId": subject_id,
                "title": title,
                "description": description,
                "evidence": evidence,
                "resolvedAt": resolved_at,
                "resolvedBy": resolved_by,
                "resolution": resolution,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_admin_alerts_response_200_alerts_item_evidence_type_0 import (
            GetApiV1AdminAlertsResponse200AlertsItemEvidenceType0,
        )

        d = src_dict.copy()
        id = d.pop("id")

        alert_type = d.pop("alertType")

        severity = d.pop("severity")

        status = d.pop("status")

        subject_type = d.pop("subjectType")

        subject_id = d.pop("subjectId")

        title = d.pop("title")

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        def _parse_evidence(data: object) -> Union["GetApiV1AdminAlertsResponse200AlertsItemEvidenceType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                evidence_type_0 = GetApiV1AdminAlertsResponse200AlertsItemEvidenceType0.from_dict(data)

                return evidence_type_0
            except:  # noqa: E722
                pass
            return cast(Union["GetApiV1AdminAlertsResponse200AlertsItemEvidenceType0", None], data)

        evidence = _parse_evidence(d.pop("evidence"))

        def _parse_resolved_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        resolved_at = _parse_resolved_at(d.pop("resolvedAt"))

        def _parse_resolved_by(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        resolved_by = _parse_resolved_by(d.pop("resolvedBy"))

        def _parse_resolution(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        resolution = _parse_resolution(d.pop("resolution"))

        created_at = d.pop("createdAt")

        updated_at = d.pop("updatedAt")

        get_api_v1_admin_alerts_response_200_alerts_item = cls(
            id=id,
            alert_type=alert_type,
            severity=severity,
            status=status,
            subject_type=subject_type,
            subject_id=subject_id,
            title=title,
            description=description,
            evidence=evidence,
            resolved_at=resolved_at,
            resolved_by=resolved_by,
            resolution=resolution,
            created_at=created_at,
            updated_at=updated_at,
        )

        return get_api_v1_admin_alerts_response_200_alerts_item
