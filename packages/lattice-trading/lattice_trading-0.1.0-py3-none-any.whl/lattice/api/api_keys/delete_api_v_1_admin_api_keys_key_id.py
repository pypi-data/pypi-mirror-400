
from __future__ import annotations

from http import HTTPStatus
from typing import Any, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_api_v1_admin_api_keys_key_id_body_type_1 import DeleteApiV1AdminApiKeysKeyIdBodyType1
from ...models.delete_api_v1_admin_api_keys_key_id_response_200 import DeleteApiV1AdminApiKeysKeyIdResponse200
from ...models.delete_api_v1_admin_api_keys_key_id_response_401 import DeleteApiV1AdminApiKeysKeyIdResponse401
from ...models.delete_api_v1_admin_api_keys_key_id_response_403 import DeleteApiV1AdminApiKeysKeyIdResponse403
from ...models.delete_api_v1_admin_api_keys_key_id_response_404 import DeleteApiV1AdminApiKeysKeyIdResponse404
from ...types import Response


def _get_kwargs(
    key_id: str,
    *,
    body: Union["DeleteApiV1AdminApiKeysKeyIdBodyType1", Any],
    x_tenant_id: str,
    idempotency_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-tenant-id"] = x_tenant_id

    headers["Idempotency-Key"] = idempotency_key

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/api/v1/admin/api-keys/{key_id}",
    }

    _body: Any | dict[str, Any]
    if isinstance(body, DeleteApiV1AdminApiKeysKeyIdBodyType1):
        _body = body.to_dict()
    else:
        _body = body

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    Any
    | DeleteApiV1AdminApiKeysKeyIdResponse200
    | DeleteApiV1AdminApiKeysKeyIdResponse401
    | DeleteApiV1AdminApiKeysKeyIdResponse403
    | DeleteApiV1AdminApiKeysKeyIdResponse404
    | None
):
    if response.status_code == HTTPStatus.OK:
        response_200 = DeleteApiV1AdminApiKeysKeyIdResponse200.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = cast(Any, None)
        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = DeleteApiV1AdminApiKeysKeyIdResponse401.from_dict(response.json())

        return response_401
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = DeleteApiV1AdminApiKeysKeyIdResponse403.from_dict(response.json())

        return response_403
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = DeleteApiV1AdminApiKeysKeyIdResponse404.from_dict(response.json())

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
    | DeleteApiV1AdminApiKeysKeyIdResponse200
    | DeleteApiV1AdminApiKeysKeyIdResponse401
    | DeleteApiV1AdminApiKeysKeyIdResponse403
    | DeleteApiV1AdminApiKeysKeyIdResponse404
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
    body: Union["DeleteApiV1AdminApiKeysKeyIdBodyType1", Any],
    x_tenant_id: str,
    idempotency_key: str,
) -> Response[
    Any
    | DeleteApiV1AdminApiKeysKeyIdResponse200
    | DeleteApiV1AdminApiKeysKeyIdResponse401
    | DeleteApiV1AdminApiKeysKeyIdResponse403
    | DeleteApiV1AdminApiKeysKeyIdResponse404
]:
    """Revoke any API key in the tenant (admin)

     Revoke any API key in the tenant (admin)

    Args:
        key_id (str):
        x_tenant_id (str):
        idempotency_key (str):
        body (Union['DeleteApiV1AdminApiKeysKeyIdBodyType1', Any]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DeleteApiV1AdminApiKeysKeyIdResponse200, DeleteApiV1AdminApiKeysKeyIdResponse401, DeleteApiV1AdminApiKeysKeyIdResponse403, DeleteApiV1AdminApiKeysKeyIdResponse404]]
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
    body: Union["DeleteApiV1AdminApiKeysKeyIdBodyType1", Any],
    x_tenant_id: str,
    idempotency_key: str,
) -> (
    Any
    | DeleteApiV1AdminApiKeysKeyIdResponse200
    | DeleteApiV1AdminApiKeysKeyIdResponse401
    | DeleteApiV1AdminApiKeysKeyIdResponse403
    | DeleteApiV1AdminApiKeysKeyIdResponse404
    | None
):
    """Revoke any API key in the tenant (admin)

     Revoke any API key in the tenant (admin)

    Args:
        key_id (str):
        x_tenant_id (str):
        idempotency_key (str):
        body (Union['DeleteApiV1AdminApiKeysKeyIdBodyType1', Any]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DeleteApiV1AdminApiKeysKeyIdResponse200, DeleteApiV1AdminApiKeysKeyIdResponse401, DeleteApiV1AdminApiKeysKeyIdResponse403, DeleteApiV1AdminApiKeysKeyIdResponse404]
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
    body: Union["DeleteApiV1AdminApiKeysKeyIdBodyType1", Any],
    x_tenant_id: str,
    idempotency_key: str,
) -> Response[
    Any
    | DeleteApiV1AdminApiKeysKeyIdResponse200
    | DeleteApiV1AdminApiKeysKeyIdResponse401
    | DeleteApiV1AdminApiKeysKeyIdResponse403
    | DeleteApiV1AdminApiKeysKeyIdResponse404
]:
    """Revoke any API key in the tenant (admin)

     Revoke any API key in the tenant (admin)

    Args:
        key_id (str):
        x_tenant_id (str):
        idempotency_key (str):
        body (Union['DeleteApiV1AdminApiKeysKeyIdBodyType1', Any]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DeleteApiV1AdminApiKeysKeyIdResponse200, DeleteApiV1AdminApiKeysKeyIdResponse401, DeleteApiV1AdminApiKeysKeyIdResponse403, DeleteApiV1AdminApiKeysKeyIdResponse404]]
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
    body: Union["DeleteApiV1AdminApiKeysKeyIdBodyType1", Any],
    x_tenant_id: str,
    idempotency_key: str,
) -> (
    Any
    | DeleteApiV1AdminApiKeysKeyIdResponse200
    | DeleteApiV1AdminApiKeysKeyIdResponse401
    | DeleteApiV1AdminApiKeysKeyIdResponse403
    | DeleteApiV1AdminApiKeysKeyIdResponse404
    | None
):
    """Revoke any API key in the tenant (admin)

     Revoke any API key in the tenant (admin)

    Args:
        key_id (str):
        x_tenant_id (str):
        idempotency_key (str):
        body (Union['DeleteApiV1AdminApiKeysKeyIdBodyType1', Any]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DeleteApiV1AdminApiKeysKeyIdResponse200, DeleteApiV1AdminApiKeysKeyIdResponse401, DeleteApiV1AdminApiKeysKeyIdResponse403, DeleteApiV1AdminApiKeysKeyIdResponse404]
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
