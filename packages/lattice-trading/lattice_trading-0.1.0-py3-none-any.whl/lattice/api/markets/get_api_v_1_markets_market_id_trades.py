
from __future__ import annotations

from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_v1_markets_market_id_trades_response_200 import GetApiV1MarketsMarketIdTradesResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    market_id: str,
    *,
    outcome_id: Unset | str = UNSET,
    limit: Unset | float = 12.0,
    x_tenant_id: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-tenant-id"] = x_tenant_id

    params: dict[str, Any] = {}

    params["outcomeId"] = outcome_id

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/markets/{market_id}/trades",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | GetApiV1MarketsMarketIdTradesResponse200 | None:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetApiV1MarketsMarketIdTradesResponse200.from_dict(response.json())

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
) -> Response[Any | GetApiV1MarketsMarketIdTradesResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    market_id: str,
    *,
    client: AuthenticatedClient | Client,
    outcome_id: Unset | str = UNSET,
    limit: Unset | float = 12.0,
    x_tenant_id: str,
) -> Response[Any | GetApiV1MarketsMarketIdTradesResponse200]:
    """List recent trades for a market

     List recent trades for a market

    Args:
        market_id (str):
        outcome_id (Union[Unset, str]):
        limit (Union[Unset, float]):  Default: 12.0.
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetApiV1MarketsMarketIdTradesResponse200]]
    """

    kwargs = _get_kwargs(
        market_id=market_id,
        outcome_id=outcome_id,
        limit=limit,
        x_tenant_id=x_tenant_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    market_id: str,
    *,
    client: AuthenticatedClient | Client,
    outcome_id: Unset | str = UNSET,
    limit: Unset | float = 12.0,
    x_tenant_id: str,
) -> Any | GetApiV1MarketsMarketIdTradesResponse200 | None:
    """List recent trades for a market

     List recent trades for a market

    Args:
        market_id (str):
        outcome_id (Union[Unset, str]):
        limit (Union[Unset, float]):  Default: 12.0.
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetApiV1MarketsMarketIdTradesResponse200]
    """

    return sync_detailed(
        market_id=market_id,
        client=client,
        outcome_id=outcome_id,
        limit=limit,
        x_tenant_id=x_tenant_id,
    ).parsed


async def asyncio_detailed(
    market_id: str,
    *,
    client: AuthenticatedClient | Client,
    outcome_id: Unset | str = UNSET,
    limit: Unset | float = 12.0,
    x_tenant_id: str,
) -> Response[Any | GetApiV1MarketsMarketIdTradesResponse200]:
    """List recent trades for a market

     List recent trades for a market

    Args:
        market_id (str):
        outcome_id (Union[Unset, str]):
        limit (Union[Unset, float]):  Default: 12.0.
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetApiV1MarketsMarketIdTradesResponse200]]
    """

    kwargs = _get_kwargs(
        market_id=market_id,
        outcome_id=outcome_id,
        limit=limit,
        x_tenant_id=x_tenant_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    market_id: str,
    *,
    client: AuthenticatedClient | Client,
    outcome_id: Unset | str = UNSET,
    limit: Unset | float = 12.0,
    x_tenant_id: str,
) -> Any | GetApiV1MarketsMarketIdTradesResponse200 | None:
    """List recent trades for a market

     List recent trades for a market

    Args:
        market_id (str):
        outcome_id (Union[Unset, str]):
        limit (Union[Unset, float]):  Default: 12.0.
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetApiV1MarketsMarketIdTradesResponse200]
    """

    return (
        await asyncio_detailed(
            market_id=market_id,
            client=client,
            outcome_id=outcome_id,
            limit=limit,
            x_tenant_id=x_tenant_id,
        )
    ).parsed
