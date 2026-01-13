
from __future__ import annotations

import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_v1_admin_audit_export_format import GetApiV1AdminAuditExportFormat
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: Unset | float = 1000.0,
    offset: Unset | float = 0.0,
    actor_type: Unset | str = UNSET,
    actor_id: Unset | str = UNSET,
    action: Unset | str = UNSET,
    resource: Unset | str = UNSET,
    resource_id: Unset | str = UNSET,
    from_: Unset | datetime.datetime = UNSET,
    to: Unset | datetime.datetime = UNSET,
    ip_address: Unset | str = UNSET,
    format_: Unset | GetApiV1AdminAuditExportFormat = GetApiV1AdminAuditExportFormat.JSON,
    x_tenant_id: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-tenant-id"] = x_tenant_id

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params["actorType"] = actor_type

    params["actorId"] = actor_id

    params["action"] = action

    params["resource"] = resource

    params["resourceId"] = resource_id

    json_from_: Unset | str = UNSET
    if not isinstance(from_, Unset):
        json_from_ = from_.isoformat()
    params["from"] = json_from_

    json_to: Unset | str = UNSET
    if not isinstance(to, Unset):
        json_to = to.isoformat()
    params["to"] = json_to

    params["ipAddress"] = ip_address

    json_format_: Unset | str = UNSET
    if not isinstance(format_, Unset):
        json_format_ = format_.value

    params["format"] = json_format_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/admin/audit/export",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | None:
    if response.status_code == HTTPStatus.OK:
        return None
    if response.status_code == HTTPStatus.BAD_REQUEST:
        return None
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        return None
    if response.status_code == HTTPStatus.FORBIDDEN:
        return None
    if response.status_code == HTTPStatus.NOT_FOUND:
        return None
    if response.status_code == HTTPStatus.CONFLICT:
        return None
    if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        return None
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        return None
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: Unset | float = 1000.0,
    offset: Unset | float = 0.0,
    actor_type: Unset | str = UNSET,
    actor_id: Unset | str = UNSET,
    action: Unset | str = UNSET,
    resource: Unset | str = UNSET,
    resource_id: Unset | str = UNSET,
    from_: Unset | datetime.datetime = UNSET,
    to: Unset | datetime.datetime = UNSET,
    ip_address: Unset | str = UNSET,
    format_: Unset | GetApiV1AdminAuditExportFormat = GetApiV1AdminAuditExportFormat.JSON,
    x_tenant_id: str,
) -> Response[Any]:
    """Export audit logs to JSON or CSV

     Export audit logs to JSON or CSV

    Args:
        limit (Union[Unset, float]):  Default: 1000.0.
        offset (Union[Unset, float]):  Default: 0.0.
        actor_type (Union[Unset, str]):
        actor_id (Union[Unset, str]):
        action (Union[Unset, str]):
        resource (Union[Unset, str]):
        resource_id (Union[Unset, str]):
        from_ (Union[Unset, datetime.datetime]):
        to (Union[Unset, datetime.datetime]):
        ip_address (Union[Unset, str]):
        format_ (Union[Unset, GetApiV1AdminAuditExportFormat]):  Default:
            GetApiV1AdminAuditExportFormat.JSON.
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        from_=from_,
        to=to,
        ip_address=ip_address,
        format_=format_,
        x_tenant_id=x_tenant_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: Unset | float = 1000.0,
    offset: Unset | float = 0.0,
    actor_type: Unset | str = UNSET,
    actor_id: Unset | str = UNSET,
    action: Unset | str = UNSET,
    resource: Unset | str = UNSET,
    resource_id: Unset | str = UNSET,
    from_: Unset | datetime.datetime = UNSET,
    to: Unset | datetime.datetime = UNSET,
    ip_address: Unset | str = UNSET,
    format_: Unset | GetApiV1AdminAuditExportFormat = GetApiV1AdminAuditExportFormat.JSON,
    x_tenant_id: str,
) -> Response[Any]:
    """Export audit logs to JSON or CSV

     Export audit logs to JSON or CSV

    Args:
        limit (Union[Unset, float]):  Default: 1000.0.
        offset (Union[Unset, float]):  Default: 0.0.
        actor_type (Union[Unset, str]):
        actor_id (Union[Unset, str]):
        action (Union[Unset, str]):
        resource (Union[Unset, str]):
        resource_id (Union[Unset, str]):
        from_ (Union[Unset, datetime.datetime]):
        to (Union[Unset, datetime.datetime]):
        ip_address (Union[Unset, str]):
        format_ (Union[Unset, GetApiV1AdminAuditExportFormat]):  Default:
            GetApiV1AdminAuditExportFormat.JSON.
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        from_=from_,
        to=to,
        ip_address=ip_address,
        format_=format_,
        x_tenant_id=x_tenant_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
