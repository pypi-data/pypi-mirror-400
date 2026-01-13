
from __future__ import annotations

from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_v1_positions_response_200 import GetApiV1PositionsResponse200
from ...models.get_api_v1_positions_status import GetApiV1PositionsStatus
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: Unset | float = 50.0,
    offset: Unset | float = 0.0,
    market_id: Unset | str = UNSET,
    outcome_id: Unset | str = UNSET,
    status: Unset | GetApiV1PositionsStatus = UNSET,
    include_zero: Unset | bool = False,
    user_id: Unset | str = UNSET,
    x_tenant_id: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-tenant-id"] = x_tenant_id

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params["marketId"] = market_id

    params["outcomeId"] = outcome_id

    json_status: Unset | str = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params["includeZero"] = include_zero

    params["userId"] = user_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/positions",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | GetApiV1PositionsResponse200 | None:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetApiV1PositionsResponse200.from_dict(response.json())

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
) -> Response[Any | GetApiV1PositionsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: Unset | float = 50.0,
    offset: Unset | float = 0.0,
    market_id: Unset | str = UNSET,
    outcome_id: Unset | str = UNSET,
    status: Unset | GetApiV1PositionsStatus = UNSET,
    include_zero: Unset | bool = False,
    user_id: Unset | str = UNSET,
    x_tenant_id: str,
) -> Response[Any | GetApiV1PositionsResponse200]:
    """List user positions

     List user positions

    Args:
        limit (Union[Unset, float]):  Default: 50.0.
        offset (Union[Unset, float]):  Default: 0.0.
        market_id (Union[Unset, str]):
        outcome_id (Union[Unset, str]):
        status (Union[Unset, GetApiV1PositionsStatus]):
        include_zero (Union[Unset, bool]):  Default: False.
        user_id (Union[Unset, str]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetApiV1PositionsResponse200]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
        market_id=market_id,
        outcome_id=outcome_id,
        status=status,
        include_zero=include_zero,
        user_id=user_id,
        x_tenant_id=x_tenant_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    limit: Unset | float = 50.0,
    offset: Unset | float = 0.0,
    market_id: Unset | str = UNSET,
    outcome_id: Unset | str = UNSET,
    status: Unset | GetApiV1PositionsStatus = UNSET,
    include_zero: Unset | bool = False,
    user_id: Unset | str = UNSET,
    x_tenant_id: str,
) -> Any | GetApiV1PositionsResponse200 | None:
    """List user positions

     List user positions

    Args:
        limit (Union[Unset, float]):  Default: 50.0.
        offset (Union[Unset, float]):  Default: 0.0.
        market_id (Union[Unset, str]):
        outcome_id (Union[Unset, str]):
        status (Union[Unset, GetApiV1PositionsStatus]):
        include_zero (Union[Unset, bool]):  Default: False.
        user_id (Union[Unset, str]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetApiV1PositionsResponse200]
    """

    return sync_detailed(
        client=client,
        limit=limit,
        offset=offset,
        market_id=market_id,
        outcome_id=outcome_id,
        status=status,
        include_zero=include_zero,
        user_id=user_id,
        x_tenant_id=x_tenant_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: Unset | float = 50.0,
    offset: Unset | float = 0.0,
    market_id: Unset | str = UNSET,
    outcome_id: Unset | str = UNSET,
    status: Unset | GetApiV1PositionsStatus = UNSET,
    include_zero: Unset | bool = False,
    user_id: Unset | str = UNSET,
    x_tenant_id: str,
) -> Response[Any | GetApiV1PositionsResponse200]:
    """List user positions

     List user positions

    Args:
        limit (Union[Unset, float]):  Default: 50.0.
        offset (Union[Unset, float]):  Default: 0.0.
        market_id (Union[Unset, str]):
        outcome_id (Union[Unset, str]):
        status (Union[Unset, GetApiV1PositionsStatus]):
        include_zero (Union[Unset, bool]):  Default: False.
        user_id (Union[Unset, str]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetApiV1PositionsResponse200]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
        market_id=market_id,
        outcome_id=outcome_id,
        status=status,
        include_zero=include_zero,
        user_id=user_id,
        x_tenant_id=x_tenant_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    limit: Unset | float = 50.0,
    offset: Unset | float = 0.0,
    market_id: Unset | str = UNSET,
    outcome_id: Unset | str = UNSET,
    status: Unset | GetApiV1PositionsStatus = UNSET,
    include_zero: Unset | bool = False,
    user_id: Unset | str = UNSET,
    x_tenant_id: str,
) -> Any | GetApiV1PositionsResponse200 | None:
    """List user positions

     List user positions

    Args:
        limit (Union[Unset, float]):  Default: 50.0.
        offset (Union[Unset, float]):  Default: 0.0.
        market_id (Union[Unset, str]):
        outcome_id (Union[Unset, str]):
        status (Union[Unset, GetApiV1PositionsStatus]):
        include_zero (Union[Unset, bool]):  Default: False.
        user_id (Union[Unset, str]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetApiV1PositionsResponse200]
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            offset=offset,
            market_id=market_id,
            outcome_id=outcome_id,
            status=status,
            include_zero=include_zero,
            user_id=user_id,
            x_tenant_id=x_tenant_id,
        )
    ).parsed
