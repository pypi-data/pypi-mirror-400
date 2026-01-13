
from __future__ import annotations

from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_v1_templates_response_200_item import GetApiV1TemplatesResponse200Item
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    category: Unset | str = UNSET,
    search: Unset | str = UNSET,
    x_tenant_id: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-tenant-id"] = x_tenant_id

    params: dict[str, Any] = {}

    params["category"] = category

    params["search"] = search

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/templates",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | list["GetApiV1TemplatesResponse200Item"] | None:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = GetApiV1TemplatesResponse200Item.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Any | list["GetApiV1TemplatesResponse200Item"]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    category: Unset | str = UNSET,
    search: Unset | str = UNSET,
    x_tenant_id: str,
) -> Response[Any | list["GetApiV1TemplatesResponse200Item"]]:
    """List sample market templates

     List sample market templates

    Args:
        category (Union[Unset, str]):
        search (Union[Unset, str]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, List['GetApiV1TemplatesResponse200Item']]]
    """

    kwargs = _get_kwargs(
        category=category,
        search=search,
        x_tenant_id=x_tenant_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    category: Unset | str = UNSET,
    search: Unset | str = UNSET,
    x_tenant_id: str,
) -> Any | list["GetApiV1TemplatesResponse200Item"] | None:
    """List sample market templates

     List sample market templates

    Args:
        category (Union[Unset, str]):
        search (Union[Unset, str]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, List['GetApiV1TemplatesResponse200Item']]
    """

    return sync_detailed(
        client=client,
        category=category,
        search=search,
        x_tenant_id=x_tenant_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    category: Unset | str = UNSET,
    search: Unset | str = UNSET,
    x_tenant_id: str,
) -> Response[Any | list["GetApiV1TemplatesResponse200Item"]]:
    """List sample market templates

     List sample market templates

    Args:
        category (Union[Unset, str]):
        search (Union[Unset, str]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, List['GetApiV1TemplatesResponse200Item']]]
    """

    kwargs = _get_kwargs(
        category=category,
        search=search,
        x_tenant_id=x_tenant_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    category: Unset | str = UNSET,
    search: Unset | str = UNSET,
    x_tenant_id: str,
) -> Any | list["GetApiV1TemplatesResponse200Item"] | None:
    """List sample market templates

     List sample market templates

    Args:
        category (Union[Unset, str]):
        search (Union[Unset, str]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, List['GetApiV1TemplatesResponse200Item']]
    """

    return (
        await asyncio_detailed(
            client=client,
            category=category,
            search=search,
            x_tenant_id=x_tenant_id,
        )
    ).parsed
