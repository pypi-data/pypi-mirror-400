
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_admin_audit_response_200_data_item_changes_type_0 import (
        GetApiV1AdminAuditResponse200DataItemChangesType0,
    )


T = TypeVar("T", bound="GetApiV1AdminAuditResponse200DataItem")


@_attrs_define
class GetApiV1AdminAuditResponse200DataItem:
    """
    Attributes:
        id (str):
        tenant_id (str):
        actor_type (str):
        actor_id (Union[None, str]):
        action (str):
        resource (str):
        resource_id (Union[None, str]):
        description (Union[None, str]):
        changes (Union['GetApiV1AdminAuditResponse200DataItemChangesType0', None]):
        ip_address (Union[None, str]):
        user_agent (Union[None, str]):
        request_id (Union[None, str]):
        created_at (str):
    """

    id: str
    tenant_id: str
    actor_type: str
    actor_id: None | str
    action: str
    resource: str
    resource_id: None | str
    description: None | str
    changes: Union["GetApiV1AdminAuditResponse200DataItemChangesType0", None]
    ip_address: None | str
    user_agent: None | str
    request_id: None | str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        from ..models.get_api_v1_admin_audit_response_200_data_item_changes_type_0 import (
            GetApiV1AdminAuditResponse200DataItemChangesType0,
        )

        id = self.id

        tenant_id = self.tenant_id

        actor_type = self.actor_type

        actor_id: None | str
        actor_id = self.actor_id

        action = self.action

        resource = self.resource

        resource_id: None | str
        resource_id = self.resource_id

        description: None | str
        description = self.description

        changes: dict[str, Any] | None
        if isinstance(self.changes, GetApiV1AdminAuditResponse200DataItemChangesType0):
            changes = self.changes.to_dict()
        else:
            changes = self.changes

        ip_address: None | str
        ip_address = self.ip_address

        user_agent: None | str
        user_agent = self.user_agent

        request_id: None | str
        request_id = self.request_id

        created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "tenantId": tenant_id,
                "actorType": actor_type,
                "actorId": actor_id,
                "action": action,
                "resource": resource,
                "resourceId": resource_id,
                "description": description,
                "changes": changes,
                "ipAddress": ip_address,
                "userAgent": user_agent,
                "requestId": request_id,
                "createdAt": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_admin_audit_response_200_data_item_changes_type_0 import (
            GetApiV1AdminAuditResponse200DataItemChangesType0,
        )

        d = src_dict.copy()
        id = d.pop("id")

        tenant_id = d.pop("tenantId")

        actor_type = d.pop("actorType")

        def _parse_actor_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        actor_id = _parse_actor_id(d.pop("actorId"))

        action = d.pop("action")

        resource = d.pop("resource")

        def _parse_resource_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        resource_id = _parse_resource_id(d.pop("resourceId"))

        def _parse_description(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        description = _parse_description(d.pop("description"))

        def _parse_changes(data: object) -> Union["GetApiV1AdminAuditResponse200DataItemChangesType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                changes_type_0 = GetApiV1AdminAuditResponse200DataItemChangesType0.from_dict(data)

                return changes_type_0
            except:  # noqa: E722
                pass
            return cast(Union["GetApiV1AdminAuditResponse200DataItemChangesType0", None], data)

        changes = _parse_changes(d.pop("changes"))

        def _parse_ip_address(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        ip_address = _parse_ip_address(d.pop("ipAddress"))

        def _parse_user_agent(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        user_agent = _parse_user_agent(d.pop("userAgent"))

        def _parse_request_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        request_id = _parse_request_id(d.pop("requestId"))

        created_at = d.pop("createdAt")

        get_api_v1_admin_audit_response_200_data_item = cls(
            id=id,
            tenant_id=tenant_id,
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            description=description,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            created_at=created_at,
        )

        return get_api_v1_admin_audit_response_200_data_item
