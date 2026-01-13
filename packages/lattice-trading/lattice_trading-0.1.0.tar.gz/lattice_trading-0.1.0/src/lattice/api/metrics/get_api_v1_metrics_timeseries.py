
from __future__ import annotations

import datetime
from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_api_v1_metrics_timeseries_interval import GetApiV1MetricsTimeseriesInterval
from ...models.get_api_v1_metrics_timeseries_metric import GetApiV1MetricsTimeseriesMetric
from ...models.get_api_v1_metrics_timeseries_response_200 import GetApiV1MetricsTimeseriesResponse200
from ...models.get_api_v1_metrics_timeseries_response_400 import GetApiV1MetricsTimeseriesResponse400
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    metric: GetApiV1MetricsTimeseriesMetric,
    start: datetime.datetime,
    end: datetime.datetime,
    interval: Unset | GetApiV1MetricsTimeseriesInterval = GetApiV1MetricsTimeseriesInterval.DAY,
    x_tenant_id: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["x-tenant-id"] = x_tenant_id

    params: dict[str, Any] = {}

    json_metric = metric.value
    params["metric"] = json_metric

    json_start = start.isoformat()
    params["start"] = json_start

    json_end = end.isoformat()
    params["end"] = json_end

    json_interval: Unset | str = UNSET
    if not isinstance(interval, Unset):
        json_interval = interval.value

    params["interval"] = json_interval

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/metrics/timeseries",
        "params": params,
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | GetApiV1MetricsTimeseriesResponse200 | GetApiV1MetricsTimeseriesResponse400 | None:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetApiV1MetricsTimeseriesResponse200.from_dict(response.json())

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = GetApiV1MetricsTimeseriesResponse400.from_dict(response.json())

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
) -> Response[Any | GetApiV1MetricsTimeseriesResponse200 | GetApiV1MetricsTimeseriesResponse400]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    metric: GetApiV1MetricsTimeseriesMetric,
    start: datetime.datetime,
    end: datetime.datetime,
    interval: Unset | GetApiV1MetricsTimeseriesInterval = GetApiV1MetricsTimeseriesInterval.DAY,
    x_tenant_id: str,
) -> Response[Any | GetApiV1MetricsTimeseriesResponse200 | GetApiV1MetricsTimeseriesResponse400]:
    """Get timeseries metrics for reporting dashboards

     Get timeseries metrics for reporting dashboards

    Args:
        metric (GetApiV1MetricsTimeseriesMetric):
        start (datetime.datetime):
        end (datetime.datetime):
        interval (Union[Unset, GetApiV1MetricsTimeseriesInterval]):  Default:
            GetApiV1MetricsTimeseriesInterval.DAY.
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetApiV1MetricsTimeseriesResponse200, GetApiV1MetricsTimeseriesResponse400]]
    """

    kwargs = _get_kwargs(
        metric=metric,
        start=start,
        end=end,
        interval=interval,
        x_tenant_id=x_tenant_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    metric: GetApiV1MetricsTimeseriesMetric,
    start: datetime.datetime,
    end: datetime.datetime,
    interval: Unset | GetApiV1MetricsTimeseriesInterval = GetApiV1MetricsTimeseriesInterval.DAY,
    x_tenant_id: str,
) -> Any | GetApiV1MetricsTimeseriesResponse200 | GetApiV1MetricsTimeseriesResponse400 | None:
    """Get timeseries metrics for reporting dashboards

     Get timeseries metrics for reporting dashboards

    Args:
        metric (GetApiV1MetricsTimeseriesMetric):
        start (datetime.datetime):
        end (datetime.datetime):
        interval (Union[Unset, GetApiV1MetricsTimeseriesInterval]):  Default:
            GetApiV1MetricsTimeseriesInterval.DAY.
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetApiV1MetricsTimeseriesResponse200, GetApiV1MetricsTimeseriesResponse400]
    """

    return sync_detailed(
        client=client,
        metric=metric,
        start=start,
        end=end,
        interval=interval,
        x_tenant_id=x_tenant_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    metric: GetApiV1MetricsTimeseriesMetric,
    start: datetime.datetime,
    end: datetime.datetime,
    interval: Unset | GetApiV1MetricsTimeseriesInterval = GetApiV1MetricsTimeseriesInterval.DAY,
    x_tenant_id: str,
) -> Response[Any | GetApiV1MetricsTimeseriesResponse200 | GetApiV1MetricsTimeseriesResponse400]:
    """Get timeseries metrics for reporting dashboards

     Get timeseries metrics for reporting dashboards

    Args:
        metric (GetApiV1MetricsTimeseriesMetric):
        start (datetime.datetime):
        end (datetime.datetime):
        interval (Union[Unset, GetApiV1MetricsTimeseriesInterval]):  Default:
            GetApiV1MetricsTimeseriesInterval.DAY.
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, GetApiV1MetricsTimeseriesResponse200, GetApiV1MetricsTimeseriesResponse400]]
    """

    kwargs = _get_kwargs(
        metric=metric,
        start=start,
        end=end,
        interval=interval,
        x_tenant_id=x_tenant_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    metric: GetApiV1MetricsTimeseriesMetric,
    start: datetime.datetime,
    end: datetime.datetime,
    interval: Unset | GetApiV1MetricsTimeseriesInterval = GetApiV1MetricsTimeseriesInterval.DAY,
    x_tenant_id: str,
) -> Any | GetApiV1MetricsTimeseriesResponse200 | GetApiV1MetricsTimeseriesResponse400 | None:
    """Get timeseries metrics for reporting dashboards

     Get timeseries metrics for reporting dashboards

    Args:
        metric (GetApiV1MetricsTimeseriesMetric):
        start (datetime.datetime):
        end (datetime.datetime):
        interval (Union[Unset, GetApiV1MetricsTimeseriesInterval]):  Default:
            GetApiV1MetricsTimeseriesInterval.DAY.
        x_tenant_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, GetApiV1MetricsTimeseriesResponse200, GetApiV1MetricsTimeseriesResponse400]
    """

    return (
        await asyncio_detailed(
            client=client,
            metric=metric,
            start=start,
            end=end,
            interval=interval,
            x_tenant_id=x_tenant_id,
        )
    ).parsed
