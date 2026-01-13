
from __future__ import annotations

from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.patch_api_v1_admin_alerts_alert_id_body import PatchApiV1AdminAlertsAlertIdBody
from ...models.patch_api_v1_admin_alerts_alert_id_response_200 import PatchApiV1AdminAlertsAlertIdResponse200
from ...models.patch_api_v1_admin_alerts_alert_id_response_400 import PatchApiV1AdminAlertsAlertIdResponse400
from ...models.patch_api_v1_admin_alerts_alert_id_response_404 import PatchApiV1AdminAlertsAlertIdResponse404
from ...types import Response


def _get_kwargs(
    alert_id: str,
    *,
    body: PatchApiV1AdminAlertsAlertIdBody,
    x_tenant_id: str,
    idempotency_key: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-tenant-id"] = x_tenant_id

    headers["Idempotency-Key"] = idempotency_key

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": f"/api/v1/admin/alerts/{alert_id}",
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
    | PatchApiV1AdminAlertsAlertIdResponse200
    | PatchApiV1AdminAlertsAlertIdResponse400
    | PatchApiV1AdminAlertsAlertIdResponse404
    | None
):
    if response.status_code == HTTPStatus.OK:
        response_200 = PatchApiV1AdminAlertsAlertIdResponse200.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = PatchApiV1AdminAlertsAlertIdResponse400.from_dict(response.json())

        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = cast(Any, None)
        return response_401
    if response.status_code == HTTPStatus.FORBIDDEN:
        response_403 = cast(Any, None)
        return response_403
    if response.status_code == HTTPStatus.NOT_FOUND:
        response_404 = PatchApiV1AdminAlertsAlertIdResponse404.from_dict(response.json())

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
    | PatchApiV1AdminAlertsAlertIdResponse200
    | PatchApiV1AdminAlertsAlertIdResponse400
    | PatchApiV1AdminAlertsAlertIdResponse404
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    alert_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PatchApiV1AdminAlertsAlertIdBody,
    x_tenant_id: str,
    idempotency_key: str,
) -> Response[
    Any
    | PatchApiV1AdminAlertsAlertIdResponse200
    | PatchApiV1AdminAlertsAlertIdResponse400
    | PatchApiV1AdminAlertsAlertIdResponse404
]:
    """Update alert status

     Update alert status

    Args:
        alert_id (str):
        x_tenant_id (str):
        idempotency_key (str):
        body (PatchApiV1AdminAlertsAlertIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PatchApiV1AdminAlertsAlertIdResponse200, PatchApiV1AdminAlertsAlertIdResponse400, PatchApiV1AdminAlertsAlertIdResponse404]]
    """

    kwargs = _get_kwargs(
        alert_id=alert_id,
        body=body,
        x_tenant_id=x_tenant_id,
        idempotency_key=idempotency_key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    alert_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PatchApiV1AdminAlertsAlertIdBody,
    x_tenant_id: str,
    idempotency_key: str,
) -> (
    Any
    | PatchApiV1AdminAlertsAlertIdResponse200
    | PatchApiV1AdminAlertsAlertIdResponse400
    | PatchApiV1AdminAlertsAlertIdResponse404
    | None
):
    """Update alert status

     Update alert status

    Args:
        alert_id (str):
        x_tenant_id (str):
        idempotency_key (str):
        body (PatchApiV1AdminAlertsAlertIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PatchApiV1AdminAlertsAlertIdResponse200, PatchApiV1AdminAlertsAlertIdResponse400, PatchApiV1AdminAlertsAlertIdResponse404]
    """

    return sync_detailed(
        alert_id=alert_id,
        client=client,
        body=body,
        x_tenant_id=x_tenant_id,
        idempotency_key=idempotency_key,
    ).parsed


async def asyncio_detailed(
    alert_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PatchApiV1AdminAlertsAlertIdBody,
    x_tenant_id: str,
    idempotency_key: str,
) -> Response[
    Any
    | PatchApiV1AdminAlertsAlertIdResponse200
    | PatchApiV1AdminAlertsAlertIdResponse400
    | PatchApiV1AdminAlertsAlertIdResponse404
]:
    """Update alert status

     Update alert status

    Args:
        alert_id (str):
        x_tenant_id (str):
        idempotency_key (str):
        body (PatchApiV1AdminAlertsAlertIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PatchApiV1AdminAlertsAlertIdResponse200, PatchApiV1AdminAlertsAlertIdResponse400, PatchApiV1AdminAlertsAlertIdResponse404]]
    """

    kwargs = _get_kwargs(
        alert_id=alert_id,
        body=body,
        x_tenant_id=x_tenant_id,
        idempotency_key=idempotency_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    alert_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PatchApiV1AdminAlertsAlertIdBody,
    x_tenant_id: str,
    idempotency_key: str,
) -> (
    Any
    | PatchApiV1AdminAlertsAlertIdResponse200
    | PatchApiV1AdminAlertsAlertIdResponse400
    | PatchApiV1AdminAlertsAlertIdResponse404
    | None
):
    """Update alert status

     Update alert status

    Args:
        alert_id (str):
        x_tenant_id (str):
        idempotency_key (str):
        body (PatchApiV1AdminAlertsAlertIdBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PatchApiV1AdminAlertsAlertIdResponse200, PatchApiV1AdminAlertsAlertIdResponse400, PatchApiV1AdminAlertsAlertIdResponse404]
    """

    return (
        await asyncio_detailed(
            alert_id=alert_id,
            client=client,
            body=body,
            x_tenant_id=x_tenant_id,
            idempotency_key=idempotency_key,
        )
    ).parsed
