
from __future__ import annotations

import datetime
from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_v1_account_statement_response_200 import GetApiV1AccountStatementResponse200
from ...types import UNSET, Response


def _get_kwargs(
    *,
    from_date: datetime.datetime,
    to_date: datetime.datetime,
    x_tenant_id: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-tenant-id"] = x_tenant_id

    params: dict[str, Any] = {}

    json_from_date = from_date.isoformat()
    params["fromDate"] = json_from_date

    json_to_date = to_date.isoformat()
    params["toDate"] = json_to_date

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/account/statement",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | GetApiV1AccountStatementResponse200 | None:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetApiV1AccountStatementResponse200.from_dict(response.json())

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
) -> Response[Any | GetApiV1AccountStatementResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    from_date: datetime.datetime,
    to_date: datetime.datetime,
    x_tenant_id: str,
) -> Response[Any | GetApiV1AccountStatementResponse200]:
    """Get account statement for a date range

     Get account statement for a date range

    Args:
        from_date (datetime.datetime):
        to_date (datetime.datetime):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetApiV1AccountStatementResponse200]]
    """

    kwargs = _get_kwargs(
        from_date=from_date,
        to_date=to_date,
        x_tenant_id=x_tenant_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    from_date: datetime.datetime,
    to_date: datetime.datetime,
    x_tenant_id: str,
) -> Any | GetApiV1AccountStatementResponse200 | None:
    """Get account statement for a date range

     Get account statement for a date range

    Args:
        from_date (datetime.datetime):
        to_date (datetime.datetime):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetApiV1AccountStatementResponse200]
    """

    return sync_detailed(
        client=client,
        from_date=from_date,
        to_date=to_date,
        x_tenant_id=x_tenant_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    from_date: datetime.datetime,
    to_date: datetime.datetime,
    x_tenant_id: str,
) -> Response[Any | GetApiV1AccountStatementResponse200]:
    """Get account statement for a date range

     Get account statement for a date range

    Args:
        from_date (datetime.datetime):
        to_date (datetime.datetime):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetApiV1AccountStatementResponse200]]
    """

    kwargs = _get_kwargs(
        from_date=from_date,
        to_date=to_date,
        x_tenant_id=x_tenant_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    from_date: datetime.datetime,
    to_date: datetime.datetime,
    x_tenant_id: str,
) -> Any | GetApiV1AccountStatementResponse200 | None:
    """Get account statement for a date range

     Get account statement for a date range

    Args:
        from_date (datetime.datetime):
        to_date (datetime.datetime):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetApiV1AccountStatementResponse200]
    """

    return (
        await asyncio_detailed(
            client=client,
            from_date=from_date,
            to_date=to_date,
            x_tenant_id=x_tenant_id,
        )
    ).parsed
