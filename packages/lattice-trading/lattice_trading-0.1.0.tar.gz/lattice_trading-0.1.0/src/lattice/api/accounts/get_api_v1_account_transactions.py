
from __future__ import annotations

import datetime
from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_v1_account_transactions_response_200 import GetApiV1AccountTransactionsResponse200
from ...models.get_api_v1_account_transactions_type import GetApiV1AccountTransactionsType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: Unset | float = 50.0,
    offset: Unset | float = 0.0,
    cursor: Unset | str = UNSET,
    type: Unset | GetApiV1AccountTransactionsType = UNSET,
    from_date: Unset | datetime.datetime = UNSET,
    to_date: Unset | datetime.datetime = UNSET,
    min_amount: Unset | float = UNSET,
    max_amount: Unset | float = UNSET,
    x_tenant_id: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-tenant-id"] = x_tenant_id

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    params["cursor"] = cursor

    json_type: Unset | str = UNSET
    if not isinstance(type, Unset):
        json_type = type.value

    params["type"] = json_type

    json_from_date: Unset | str = UNSET
    if not isinstance(from_date, Unset):
        json_from_date = from_date.isoformat()
    params["fromDate"] = json_from_date

    json_to_date: Unset | str = UNSET
    if not isinstance(to_date, Unset):
        json_to_date = to_date.isoformat()
    params["toDate"] = json_to_date

    params["minAmount"] = min_amount

    params["maxAmount"] = max_amount

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/account/transactions",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | GetApiV1AccountTransactionsResponse200 | None:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetApiV1AccountTransactionsResponse200.from_dict(response.json())

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
) -> Response[Any | GetApiV1AccountTransactionsResponse200]:
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
    cursor: Unset | str = UNSET,
    type: Unset | GetApiV1AccountTransactionsType = UNSET,
    from_date: Unset | datetime.datetime = UNSET,
    to_date: Unset | datetime.datetime = UNSET,
    min_amount: Unset | float = UNSET,
    max_amount: Unset | float = UNSET,
    x_tenant_id: str,
) -> Response[Any | GetApiV1AccountTransactionsResponse200]:
    """Get account transaction history

     Get account transaction history

    Args:
        limit (Union[Unset, float]):  Default: 50.0.
        offset (Union[Unset, float]):  Default: 0.0.
        cursor (Union[Unset, str]):
        type (Union[Unset, GetApiV1AccountTransactionsType]):
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        min_amount (Union[Unset, float]):
        max_amount (Union[Unset, float]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetApiV1AccountTransactionsResponse200]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
        cursor=cursor,
        type=type,
        from_date=from_date,
        to_date=to_date,
        min_amount=min_amount,
        max_amount=max_amount,
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
    cursor: Unset | str = UNSET,
    type: Unset | GetApiV1AccountTransactionsType = UNSET,
    from_date: Unset | datetime.datetime = UNSET,
    to_date: Unset | datetime.datetime = UNSET,
    min_amount: Unset | float = UNSET,
    max_amount: Unset | float = UNSET,
    x_tenant_id: str,
) -> Any | GetApiV1AccountTransactionsResponse200 | None:
    """Get account transaction history

     Get account transaction history

    Args:
        limit (Union[Unset, float]):  Default: 50.0.
        offset (Union[Unset, float]):  Default: 0.0.
        cursor (Union[Unset, str]):
        type (Union[Unset, GetApiV1AccountTransactionsType]):
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        min_amount (Union[Unset, float]):
        max_amount (Union[Unset, float]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetApiV1AccountTransactionsResponse200]
    """

    return sync_detailed(
        client=client,
        limit=limit,
        offset=offset,
        cursor=cursor,
        type=type,
        from_date=from_date,
        to_date=to_date,
        min_amount=min_amount,
        max_amount=max_amount,
        x_tenant_id=x_tenant_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: Unset | float = 50.0,
    offset: Unset | float = 0.0,
    cursor: Unset | str = UNSET,
    type: Unset | GetApiV1AccountTransactionsType = UNSET,
    from_date: Unset | datetime.datetime = UNSET,
    to_date: Unset | datetime.datetime = UNSET,
    min_amount: Unset | float = UNSET,
    max_amount: Unset | float = UNSET,
    x_tenant_id: str,
) -> Response[Any | GetApiV1AccountTransactionsResponse200]:
    """Get account transaction history

     Get account transaction history

    Args:
        limit (Union[Unset, float]):  Default: 50.0.
        offset (Union[Unset, float]):  Default: 0.0.
        cursor (Union[Unset, str]):
        type (Union[Unset, GetApiV1AccountTransactionsType]):
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        min_amount (Union[Unset, float]):
        max_amount (Union[Unset, float]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetApiV1AccountTransactionsResponse200]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
        cursor=cursor,
        type=type,
        from_date=from_date,
        to_date=to_date,
        min_amount=min_amount,
        max_amount=max_amount,
        x_tenant_id=x_tenant_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    limit: Unset | float = 50.0,
    offset: Unset | float = 0.0,
    cursor: Unset | str = UNSET,
    type: Unset | GetApiV1AccountTransactionsType = UNSET,
    from_date: Unset | datetime.datetime = UNSET,
    to_date: Unset | datetime.datetime = UNSET,
    min_amount: Unset | float = UNSET,
    max_amount: Unset | float = UNSET,
    x_tenant_id: str,
) -> Any | GetApiV1AccountTransactionsResponse200 | None:
    """Get account transaction history

     Get account transaction history

    Args:
        limit (Union[Unset, float]):  Default: 50.0.
        offset (Union[Unset, float]):  Default: 0.0.
        cursor (Union[Unset, str]):
        type (Union[Unset, GetApiV1AccountTransactionsType]):
        from_date (Union[Unset, datetime.datetime]):
        to_date (Union[Unset, datetime.datetime]):
        min_amount (Union[Unset, float]):
        max_amount (Union[Unset, float]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetApiV1AccountTransactionsResponse200]
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            offset=offset,
            cursor=cursor,
            type=type,
            from_date=from_date,
            to_date=to_date,
            min_amount=min_amount,
            max_amount=max_amount,
            x_tenant_id=x_tenant_id,
        )
    ).parsed
