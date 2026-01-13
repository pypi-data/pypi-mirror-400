
from __future__ import annotations

from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.post_api_v1_api_keys_key_id_rotate_body import PostApiV1ApiKeysKeyIdRotateBody
from ...models.post_api_v1_api_keys_key_id_rotate_response_200 import PostApiV1ApiKeysKeyIdRotateResponse200
from ...models.post_api_v1_api_keys_key_id_rotate_response_401 import PostApiV1ApiKeysKeyIdRotateResponse401
from ...models.post_api_v1_api_keys_key_id_rotate_response_403 import PostApiV1ApiKeysKeyIdRotateResponse403
from ...models.post_api_v1_api_keys_key_id_rotate_response_404 import PostApiV1ApiKeysKeyIdRotateResponse404
from ...types import Response


def _get_kwargs(
    key_id: str,
    *,
    body: PostApiV1ApiKeysKeyIdRotateBody,
    x_tenant_id: str,
    idempotency_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-tenant-id"] = x_tenant_id

    headers["Idempotency-Key"] = idempotency_key

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/api/v1/api-keys/{key_id}/rotate",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    Any
    | PostApiV1ApiKeysKeyIdRotateResponse200
    | PostApiV1ApiKeysKeyIdRotateResponse401
    | PostApiV1ApiKeysKeyIdRotateResponse403
    | PostApiV1ApiKeysKeyIdRotateResponse404
    | None
):
    if response.status_code == HTTPStatus.OK:
        response_200 = PostApiV1ApiKeysKeyIdRotateResponse200.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = cast(Any, None)
        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = PostApiV1ApiKeysKeyIdRotateResponse401.from_dict(response.json())

        return response_401
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = PostApiV1ApiKeysKeyIdRotateResponse403.from_dict(response.json())

        return response_403
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = PostApiV1ApiKeysKeyIdRotateResponse404.from_dict(response.json())

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
) -> Response[
    Any
    | PostApiV1ApiKeysKeyIdRotateResponse200
    | PostApiV1ApiKeysKeyIdRotateResponse401
    | PostApiV1ApiKeysKeyIdRotateResponse403
    | PostApiV1ApiKeysKeyIdRotateResponse404
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    key_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1ApiKeysKeyIdRotateBody,
    x_tenant_id: str,
    idempotency_key: str,
) -> Response[
    Any
    | PostApiV1ApiKeysKeyIdRotateResponse200
    | PostApiV1ApiKeysKeyIdRotateResponse401
    | PostApiV1ApiKeysKeyIdRotateResponse403
    | PostApiV1ApiKeysKeyIdRotateResponse404
]:
    """Rotate an API key (creates new key, old key expires after grace period)

     Rotate an API key (creates new key, old key expires after grace period)

    Args:
        key_id (str):
        x_tenant_id (str):
        idempotency_key (str):
        body (PostApiV1ApiKeysKeyIdRotateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PostApiV1ApiKeysKeyIdRotateResponse200, PostApiV1ApiKeysKeyIdRotateResponse401, PostApiV1ApiKeysKeyIdRotateResponse403, PostApiV1ApiKeysKeyIdRotateResponse404]]
    """

    kwargs = _get_kwargs(
        key_id=key_id,
        body=body,
        x_tenant_id=x_tenant_id,
        idempotency_key=idempotency_key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    key_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1ApiKeysKeyIdRotateBody,
    x_tenant_id: str,
    idempotency_key: str,
) -> (
    Any
    | PostApiV1ApiKeysKeyIdRotateResponse200
    | PostApiV1ApiKeysKeyIdRotateResponse401
    | PostApiV1ApiKeysKeyIdRotateResponse403
    | PostApiV1ApiKeysKeyIdRotateResponse404
    | None
):
    """Rotate an API key (creates new key, old key expires after grace period)

     Rotate an API key (creates new key, old key expires after grace period)

    Args:
        key_id (str):
        x_tenant_id (str):
        idempotency_key (str):
        body (PostApiV1ApiKeysKeyIdRotateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PostApiV1ApiKeysKeyIdRotateResponse200, PostApiV1ApiKeysKeyIdRotateResponse401, PostApiV1ApiKeysKeyIdRotateResponse403, PostApiV1ApiKeysKeyIdRotateResponse404]
    """

    return sync_detailed(
        key_id=key_id,
        client=client,
        body=body,
        x_tenant_id=x_tenant_id,
        idempotency_key=idempotency_key,
    ).parsed


async def asyncio_detailed(
    key_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1ApiKeysKeyIdRotateBody,
    x_tenant_id: str,
    idempotency_key: str,
) -> Response[
    Any
    | PostApiV1ApiKeysKeyIdRotateResponse200
    | PostApiV1ApiKeysKeyIdRotateResponse401
    | PostApiV1ApiKeysKeyIdRotateResponse403
    | PostApiV1ApiKeysKeyIdRotateResponse404
]:
    """Rotate an API key (creates new key, old key expires after grace period)

     Rotate an API key (creates new key, old key expires after grace period)

    Args:
        key_id (str):
        x_tenant_id (str):
        idempotency_key (str):
        body (PostApiV1ApiKeysKeyIdRotateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PostApiV1ApiKeysKeyIdRotateResponse200, PostApiV1ApiKeysKeyIdRotateResponse401, PostApiV1ApiKeysKeyIdRotateResponse403, PostApiV1ApiKeysKeyIdRotateResponse404]]
    """

    kwargs = _get_kwargs(
        key_id=key_id,
        body=body,
        x_tenant_id=x_tenant_id,
        idempotency_key=idempotency_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    key_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PostApiV1ApiKeysKeyIdRotateBody,
    x_tenant_id: str,
    idempotency_key: str,
) -> (
    Any
    | PostApiV1ApiKeysKeyIdRotateResponse200
    | PostApiV1ApiKeysKeyIdRotateResponse401
    | PostApiV1ApiKeysKeyIdRotateResponse403
    | PostApiV1ApiKeysKeyIdRotateResponse404
    | None
):
    """Rotate an API key (creates new key, old key expires after grace period)

     Rotate an API key (creates new key, old key expires after grace period)

    Args:
        key_id (str):
        x_tenant_id (str):
        idempotency_key (str):
        body (PostApiV1ApiKeysKeyIdRotateBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PostApiV1ApiKeysKeyIdRotateResponse200, PostApiV1ApiKeysKeyIdRotateResponse401, PostApiV1ApiKeysKeyIdRotateResponse403, PostApiV1ApiKeysKeyIdRotateResponse404]
    """

    return (
        await asyncio_detailed(
            key_id=key_id,
            client=client,
            body=body,
            x_tenant_id=x_tenant_id,
            idempotency_key=idempotency_key,
        )
    ).parsed
