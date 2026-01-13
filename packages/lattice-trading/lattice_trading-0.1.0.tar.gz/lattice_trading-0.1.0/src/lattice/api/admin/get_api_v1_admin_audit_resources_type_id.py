
from __future__ import annotations

import datetime
from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_v1_admin_audit_resources_type_id_response_200 import GetApiV1AdminAuditResourcesTypeIdResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    type: str,
    id: str,
    *,
    limit: Unset | float = 100.0,
    offset: Unset | float = 0.0,
    action: Unset | str = UNSET,
    from_: Unset | datetime.datetime = UNSET,
    to: Unset | datetime.datetime = UNSET,
    ip_address: Unset | str = UNSET,
    x_tenant_id: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-tenant-id"] = x_tenant_id

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params["action"] = action

    json_from_: Unset | str = UNSET
    if not isinstance(from_, Unset):
        json_from_ = from_.isoformat()
    params["from"] = json_from_

    json_to: Unset | str = UNSET
    if not isinstance(to, Unset):
        json_to = to.isoformat()
    params["to"] = json_to

    params["ipAddress"] = ip_address

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/admin/audit/resources/{type}/{id}",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | GetApiV1AdminAuditResourcesTypeIdResponse200 | None:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetApiV1AdminAuditResourcesTypeIdResponse200.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = cast(Any, None)
        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = cast(Any, None)
        return response_403
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = cast(Any, None)
        return response_404
    if response.status_code == HTTPStatus.CONFLICT:
        response_409 = cast(Any, None)
        return response_409
    if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        response_429 = cast(Any, None)
        return response_429
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = cast(Any, None)
        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | GetApiV1AdminAuditResourcesTypeIdResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    type: str,
    id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: Unset | float = 100.0,
    offset: Unset | float = 0.0,
    action: Unset | str = UNSET,
    from_: Unset | datetime.datetime = UNSET,
    to: Unset | datetime.datetime = UNSET,
    ip_address: Unset | str = UNSET,
    x_tenant_id: str,
) -> Response[Any | GetApiV1AdminAuditResourcesTypeIdResponse200]:
    """Get audit history for a resource

     Get audit history for a resource

    Args:
        type (str):
        id (str):
        limit (Union[Unset, float]):  Default: 100.0.
        offset (Union[Unset, float]):  Default: 0.0.
        action (Union[Unset, str]):
        from_ (Union[Unset, datetime.datetime]):
        to (Union[Unset, datetime.datetime]):
        ip_address (Union[Unset, str]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetApiV1AdminAuditResourcesTypeIdResponse200]]
    """

    kwargs = _get_kwargs(
        type=type,
        id=id,
        limit=limit,
        offset=offset,
        action=action,
        from_=from_,
        to=to,
        ip_address=ip_address,
        x_tenant_id=x_tenant_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    type: str,
    id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: Unset | float = 100.0,
    offset: Unset | float = 0.0,
    action: Unset | str = UNSET,
    from_: Unset | datetime.datetime = UNSET,
    to: Unset | datetime.datetime = UNSET,
    ip_address: Unset | str = UNSET,
    x_tenant_id: str,
) -> Any | GetApiV1AdminAuditResourcesTypeIdResponse200 | None:
    """Get audit history for a resource

     Get audit history for a resource

    Args:
        type (str):
        id (str):
        limit (Union[Unset, float]):  Default: 100.0.
        offset (Union[Unset, float]):  Default: 0.0.
        action (Union[Unset, str]):
        from_ (Union[Unset, datetime.datetime]):
        to (Union[Unset, datetime.datetime]):
        ip_address (Union[Unset, str]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetApiV1AdminAuditResourcesTypeIdResponse200]
    """

    return sync_detailed(
        type=type,
        id=id,
        client=client,
        limit=limit,
        offset=offset,
        action=action,
        from_=from_,
        to=to,
        ip_address=ip_address,
        x_tenant_id=x_tenant_id,
    ).parsed


async def asyncio_detailed(
    type: str,
    id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: Unset | float = 100.0,
    offset: Unset | float = 0.0,
    action: Unset | str = UNSET,
    from_: Unset | datetime.datetime = UNSET,
    to: Unset | datetime.datetime = UNSET,
    ip_address: Unset | str = UNSET,
    x_tenant_id: str,
) -> Response[Any | GetApiV1AdminAuditResourcesTypeIdResponse200]:
    """Get audit history for a resource

     Get audit history for a resource

    Args:
        type (str):
        id (str):
        limit (Union[Unset, float]):  Default: 100.0.
        offset (Union[Unset, float]):  Default: 0.0.
        action (Union[Unset, str]):
        from_ (Union[Unset, datetime.datetime]):
        to (Union[Unset, datetime.datetime]):
        ip_address (Union[Unset, str]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetApiV1AdminAuditResourcesTypeIdResponse200]]
    """

    kwargs = _get_kwargs(
        type=type,
        id=id,
        limit=limit,
        offset=offset,
        action=action,
        from_=from_,
        to=to,
        ip_address=ip_address,
        x_tenant_id=x_tenant_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    type: str,
    id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: Unset | float = 100.0,
    offset: Unset | float = 0.0,
    action: Unset | str = UNSET,
    from_: Unset | datetime.datetime = UNSET,
    to: Unset | datetime.datetime = UNSET,
    ip_address: Unset | str = UNSET,
    x_tenant_id: str,
) -> Any | GetApiV1AdminAuditResourcesTypeIdResponse200 | None:
    """Get audit history for a resource

     Get audit history for a resource

    Args:
        type (str):
        id (str):
        limit (Union[Unset, float]):  Default: 100.0.
        offset (Union[Unset, float]):  Default: 0.0.
        action (Union[Unset, str]):
        from_ (Union[Unset, datetime.datetime]):
        to (Union[Unset, datetime.datetime]):
        ip_address (Union[Unset, str]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetApiV1AdminAuditResourcesTypeIdResponse200]
    """

    return (
        await asyncio_detailed(
            type=type,
            id=id,
            client=client,
            limit=limit,
            offset=offset,
            action=action,
            from_=from_,
            to=to,
            ip_address=ip_address,
            x_tenant_id=x_tenant_id,
        )
    ).parsed
