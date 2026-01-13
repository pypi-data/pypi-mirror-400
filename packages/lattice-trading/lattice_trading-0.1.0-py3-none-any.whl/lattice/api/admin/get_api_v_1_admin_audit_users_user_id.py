
from __future__ import annotations

import datetime
from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_v1_admin_audit_users_user_id_response_200 import GetApiV1AdminAuditUsersUserIdResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    user_id: str,
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
        "url": f"/api/v1/admin/audit/users/{user_id}",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | GetApiV1AdminAuditUsersUserIdResponse200 | None:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetApiV1AdminAuditUsersUserIdResponse200.from_dict(response.json())

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
) -> Response[Any | GetApiV1AdminAuditUsersUserIdResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: Unset | float = 100.0,
    offset: Unset | float = 0.0,
    action: Unset | str = UNSET,
    from_: Unset | datetime.datetime = UNSET,
    to: Unset | datetime.datetime = UNSET,
    ip_address: Unset | str = UNSET,
    x_tenant_id: str,
) -> Response[Any | GetApiV1AdminAuditUsersUserIdResponse200]:
    """Get audit history for a user

     Get audit history for a user

    Args:
        user_id (str):
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
        Response[Union[Any, GetApiV1AdminAuditUsersUserIdResponse200]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
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
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: Unset | float = 100.0,
    offset: Unset | float = 0.0,
    action: Unset | str = UNSET,
    from_: Unset | datetime.datetime = UNSET,
    to: Unset | datetime.datetime = UNSET,
    ip_address: Unset | str = UNSET,
    x_tenant_id: str,
) -> Any | GetApiV1AdminAuditUsersUserIdResponse200 | None:
    """Get audit history for a user

     Get audit history for a user

    Args:
        user_id (str):
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
        Union[Any, GetApiV1AdminAuditUsersUserIdResponse200]
    """

    return sync_detailed(
        user_id=user_id,
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
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: Unset | float = 100.0,
    offset: Unset | float = 0.0,
    action: Unset | str = UNSET,
    from_: Unset | datetime.datetime = UNSET,
    to: Unset | datetime.datetime = UNSET,
    ip_address: Unset | str = UNSET,
    x_tenant_id: str,
) -> Response[Any | GetApiV1AdminAuditUsersUserIdResponse200]:
    """Get audit history for a user

     Get audit history for a user

    Args:
        user_id (str):
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
        Response[Union[Any, GetApiV1AdminAuditUsersUserIdResponse200]]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
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
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: Unset | float = 100.0,
    offset: Unset | float = 0.0,
    action: Unset | str = UNSET,
    from_: Unset | datetime.datetime = UNSET,
    to: Unset | datetime.datetime = UNSET,
    ip_address: Unset | str = UNSET,
    x_tenant_id: str,
) -> Any | GetApiV1AdminAuditUsersUserIdResponse200 | None:
    """Get audit history for a user

     Get audit history for a user

    Args:
        user_id (str):
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
        Union[Any, GetApiV1AdminAuditUsersUserIdResponse200]
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
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
