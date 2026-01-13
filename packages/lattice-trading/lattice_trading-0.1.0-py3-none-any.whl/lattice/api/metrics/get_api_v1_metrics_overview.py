
from __future__ import annotations

from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_v1_metrics_overview_response_200 import GetApiV1MetricsOverviewResponse200
from ...types import Response


def _get_kwargs(
    *,
    x_tenant_id: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-tenant-id"] = x_tenant_id

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/metrics/overview",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | GetApiV1MetricsOverviewResponse200 | None:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetApiV1MetricsOverviewResponse200.from_dict(response.json())

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
) -> Response[Any | GetApiV1MetricsOverviewResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    x_tenant_id: str,
) -> Response[Any | GetApiV1MetricsOverviewResponse200]:
    """Get aggregate market metrics for the tenant

     Get aggregate market metrics for the tenant

    Args:
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetApiV1MetricsOverviewResponse200]]
    """

    kwargs = _get_kwargs(
        x_tenant_id=x_tenant_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    x_tenant_id: str,
) -> Any | GetApiV1MetricsOverviewResponse200 | None:
    """Get aggregate market metrics for the tenant

     Get aggregate market metrics for the tenant

    Args:
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetApiV1MetricsOverviewResponse200]
    """

    return sync_detailed(
        client=client,
        x_tenant_id=x_tenant_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    x_tenant_id: str,
) -> Response[Any | GetApiV1MetricsOverviewResponse200]:
    """Get aggregate market metrics for the tenant

     Get aggregate market metrics for the tenant

    Args:
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetApiV1MetricsOverviewResponse200]]
    """

    kwargs = _get_kwargs(
        x_tenant_id=x_tenant_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    x_tenant_id: str,
) -> Any | GetApiV1MetricsOverviewResponse200 | None:
    """Get aggregate market metrics for the tenant

     Get aggregate market metrics for the tenant

    Args:
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetApiV1MetricsOverviewResponse200]
    """

    return (
        await asyncio_detailed(
            client=client,
            x_tenant_id=x_tenant_id,
        )
    ).parsed
