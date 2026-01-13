
from __future__ import annotations

import datetime
from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_v1_admin_alerts_alert_type import GetApiV1AdminAlertsAlertType
from ...models.get_api_v1_admin_alerts_response_200 import GetApiV1AdminAlertsResponse200
from ...models.get_api_v1_admin_alerts_severity import GetApiV1AdminAlertsSeverity
from ...models.get_api_v1_admin_alerts_status import GetApiV1AdminAlertsStatus
from ...models.get_api_v1_admin_alerts_subject_type import GetApiV1AdminAlertsSubjectType
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: Unset | float = 50.0,
    offset: Unset | float = 0.0,
    alert_type: Unset | GetApiV1AdminAlertsAlertType = UNSET,
    severity: Unset | GetApiV1AdminAlertsSeverity = UNSET,
    status: Unset | GetApiV1AdminAlertsStatus = UNSET,
    subject_type: Unset | GetApiV1AdminAlertsSubjectType = UNSET,
    subject_id: Unset | str = UNSET,
    from_: Unset | datetime.datetime = UNSET,
    to: Unset | datetime.datetime = UNSET,
    x_tenant_id: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-tenant-id"] = x_tenant_id

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    json_alert_type: Unset | str = UNSET
    if not isinstance(alert_type, Unset):
        json_alert_type = alert_type.value

    params["alertType"] = json_alert_type

    json_severity: Unset | str = UNSET
    if not isinstance(severity, Unset):
        json_severity = severity.value

    params["severity"] = json_severity

    json_status: Unset | str = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    json_subject_type: Unset | str = UNSET
    if not isinstance(subject_type, Unset):
        json_subject_type = subject_type.value

    params["subjectType"] = json_subject_type

    params["subjectId"] = subject_id

    json_from_: Unset | str = UNSET
    if not isinstance(from_, Unset):
        json_from_ = from_.isoformat()
    params["from"] = json_from_

    json_to: Unset | str = UNSET
    if not isinstance(to, Unset):
        json_to = to.isoformat()
    params["to"] = json_to

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/admin/alerts",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | GetApiV1AdminAlertsResponse200 | None:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetApiV1AdminAlertsResponse200.from_dict(response.json())

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
) -> Response[Any | GetApiV1AdminAlertsResponse200]:
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
    alert_type: Unset | GetApiV1AdminAlertsAlertType = UNSET,
    severity: Unset | GetApiV1AdminAlertsSeverity = UNSET,
    status: Unset | GetApiV1AdminAlertsStatus = UNSET,
    subject_type: Unset | GetApiV1AdminAlertsSubjectType = UNSET,
    subject_id: Unset | str = UNSET,
    from_: Unset | datetime.datetime = UNSET,
    to: Unset | datetime.datetime = UNSET,
    x_tenant_id: str,
) -> Response[Any | GetApiV1AdminAlertsResponse200]:
    """List compliance alerts with filtering

     List compliance alerts with filtering

    Args:
        limit (Union[Unset, float]):  Default: 50.0.
        offset (Union[Unset, float]):  Default: 0.0.
        alert_type (Union[Unset, GetApiV1AdminAlertsAlertType]):
        severity (Union[Unset, GetApiV1AdminAlertsSeverity]):
        status (Union[Unset, GetApiV1AdminAlertsStatus]):
        subject_type (Union[Unset, GetApiV1AdminAlertsSubjectType]):
        subject_id (Union[Unset, str]):
        from_ (Union[Unset, datetime.datetime]):
        to (Union[Unset, datetime.datetime]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetApiV1AdminAlertsResponse200]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
        alert_type=alert_type,
        severity=severity,
        status=status,
        subject_type=subject_type,
        subject_id=subject_id,
        from_=from_,
        to=to,
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
    alert_type: Unset | GetApiV1AdminAlertsAlertType = UNSET,
    severity: Unset | GetApiV1AdminAlertsSeverity = UNSET,
    status: Unset | GetApiV1AdminAlertsStatus = UNSET,
    subject_type: Unset | GetApiV1AdminAlertsSubjectType = UNSET,
    subject_id: Unset | str = UNSET,
    from_: Unset | datetime.datetime = UNSET,
    to: Unset | datetime.datetime = UNSET,
    x_tenant_id: str,
) -> Any | GetApiV1AdminAlertsResponse200 | None:
    """List compliance alerts with filtering

     List compliance alerts with filtering

    Args:
        limit (Union[Unset, float]):  Default: 50.0.
        offset (Union[Unset, float]):  Default: 0.0.
        alert_type (Union[Unset, GetApiV1AdminAlertsAlertType]):
        severity (Union[Unset, GetApiV1AdminAlertsSeverity]):
        status (Union[Unset, GetApiV1AdminAlertsStatus]):
        subject_type (Union[Unset, GetApiV1AdminAlertsSubjectType]):
        subject_id (Union[Unset, str]):
        from_ (Union[Unset, datetime.datetime]):
        to (Union[Unset, datetime.datetime]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetApiV1AdminAlertsResponse200]
    """

    return sync_detailed(
        client=client,
        limit=limit,
        offset=offset,
        alert_type=alert_type,
        severity=severity,
        status=status,
        subject_type=subject_type,
        subject_id=subject_id,
        from_=from_,
        to=to,
        x_tenant_id=x_tenant_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: Unset | float = 50.0,
    offset: Unset | float = 0.0,
    alert_type: Unset | GetApiV1AdminAlertsAlertType = UNSET,
    severity: Unset | GetApiV1AdminAlertsSeverity = UNSET,
    status: Unset | GetApiV1AdminAlertsStatus = UNSET,
    subject_type: Unset | GetApiV1AdminAlertsSubjectType = UNSET,
    subject_id: Unset | str = UNSET,
    from_: Unset | datetime.datetime = UNSET,
    to: Unset | datetime.datetime = UNSET,
    x_tenant_id: str,
) -> Response[Any | GetApiV1AdminAlertsResponse200]:
    """List compliance alerts with filtering

     List compliance alerts with filtering

    Args:
        limit (Union[Unset, float]):  Default: 50.0.
        offset (Union[Unset, float]):  Default: 0.0.
        alert_type (Union[Unset, GetApiV1AdminAlertsAlertType]):
        severity (Union[Unset, GetApiV1AdminAlertsSeverity]):
        status (Union[Unset, GetApiV1AdminAlertsStatus]):
        subject_type (Union[Unset, GetApiV1AdminAlertsSubjectType]):
        subject_id (Union[Unset, str]):
        from_ (Union[Unset, datetime.datetime]):
        to (Union[Unset, datetime.datetime]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetApiV1AdminAlertsResponse200]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
        alert_type=alert_type,
        severity=severity,
        status=status,
        subject_type=subject_type,
        subject_id=subject_id,
        from_=from_,
        to=to,
        x_tenant_id=x_tenant_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    limit: Unset | float = 50.0,
    offset: Unset | float = 0.0,
    alert_type: Unset | GetApiV1AdminAlertsAlertType = UNSET,
    severity: Unset | GetApiV1AdminAlertsSeverity = UNSET,
    status: Unset | GetApiV1AdminAlertsStatus = UNSET,
    subject_type: Unset | GetApiV1AdminAlertsSubjectType = UNSET,
    subject_id: Unset | str = UNSET,
    from_: Unset | datetime.datetime = UNSET,
    to: Unset | datetime.datetime = UNSET,
    x_tenant_id: str,
) -> Any | GetApiV1AdminAlertsResponse200 | None:
    """List compliance alerts with filtering

     List compliance alerts with filtering

    Args:
        limit (Union[Unset, float]):  Default: 50.0.
        offset (Union[Unset, float]):  Default: 0.0.
        alert_type (Union[Unset, GetApiV1AdminAlertsAlertType]):
        severity (Union[Unset, GetApiV1AdminAlertsSeverity]):
        status (Union[Unset, GetApiV1AdminAlertsStatus]):
        subject_type (Union[Unset, GetApiV1AdminAlertsSubjectType]):
        subject_id (Union[Unset, str]):
        from_ (Union[Unset, datetime.datetime]):
        to (Union[Unset, datetime.datetime]):
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetApiV1AdminAlertsResponse200]
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            offset=offset,
            alert_type=alert_type,
            severity=severity,
            status=status,
            subject_type=subject_type,
            subject_id=subject_id,
            from_=from_,
            to=to,
            x_tenant_id=x_tenant_id,
        )
    ).parsed
