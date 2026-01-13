
from __future__ import annotations

from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_api_v1_templates_id_apply_body import PostApiV1TemplatesIdApplyBody
from ...models.post_api_v1_templates_id_apply_response_201 import PostApiV1TemplatesIdApplyResponse201
from ...models.post_api_v1_templates_id_apply_response_400 import PostApiV1TemplatesIdApplyResponse400
from ...types import Response


def _get_kwargs(
    id: str,
    *,
    body: PostApiV1TemplatesIdApplyBody,
    x_tenant_id: str,
    idempotency_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-tenant-id"] = x_tenant_id

    headers["Idempotency-Key"] = idempotency_key

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/templates/{id}/apply",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | PostApiV1TemplatesIdApplyResponse201 | PostApiV1TemplatesIdApplyResponse400 | None:
    if response.status_code == HTTPStatus.CREATED:
        response_201 = PostApiV1TemplatesIdApplyResponse201.from_dict(response.json())

        return response_201
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = PostApiV1TemplatesIdApplyResponse400.from_dict(response.json())

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
) -> Response[Any | PostApiV1TemplatesIdApplyResponse201 | PostApiV1TemplatesIdApplyResponse400]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1TemplatesIdApplyBody,
    x_tenant_id: str,
    idempotency_key: str,
) -> Response[Any | PostApiV1TemplatesIdApplyResponse201 | PostApiV1TemplatesIdApplyResponse400]:
    """Create a market from a template

     Create a market from a template

    Args:
        id (str):
        x_tenant_id (str):
        idempotency_key (str):
        body (PostApiV1TemplatesIdApplyBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PostApiV1TemplatesIdApplyResponse201, PostApiV1TemplatesIdApplyResponse400]]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
        x_tenant_id=x_tenant_id,
        idempotency_key=idempotency_key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1TemplatesIdApplyBody,
    x_tenant_id: str,
    idempotency_key: str,
) -> Any | PostApiV1TemplatesIdApplyResponse201 | PostApiV1TemplatesIdApplyResponse400 | None:
    """Create a market from a template

     Create a market from a template

    Args:
        id (str):
        x_tenant_id (str):
        idempotency_key (str):
        body (PostApiV1TemplatesIdApplyBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PostApiV1TemplatesIdApplyResponse201, PostApiV1TemplatesIdApplyResponse400]
    """

    return sync_detailed(
        id=id,
        client=client,
        body=body,
        x_tenant_id=x_tenant_id,
        idempotency_key=idempotency_key,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1TemplatesIdApplyBody,
    x_tenant_id: str,
    idempotency_key: str,
) -> Response[Any | PostApiV1TemplatesIdApplyResponse201 | PostApiV1TemplatesIdApplyResponse400]:
    """Create a market from a template

     Create a market from a template

    Args:
        id (str):
        x_tenant_id (str):
        idempotency_key (str):
        body (PostApiV1TemplatesIdApplyBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PostApiV1TemplatesIdApplyResponse201, PostApiV1TemplatesIdApplyResponse400]]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
        x_tenant_id=x_tenant_id,
        idempotency_key=idempotency_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1TemplatesIdApplyBody,
    x_tenant_id: str,
    idempotency_key: str,
) -> Any | PostApiV1TemplatesIdApplyResponse201 | PostApiV1TemplatesIdApplyResponse400 | None:
    """Create a market from a template

     Create a market from a template

    Args:
        id (str):
        x_tenant_id (str):
        idempotency_key (str):
        body (PostApiV1TemplatesIdApplyBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PostApiV1TemplatesIdApplyResponse201, PostApiV1TemplatesIdApplyResponse400]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
            x_tenant_id=x_tenant_id,
            idempotency_key=idempotency_key,
        )
    ).parsed
