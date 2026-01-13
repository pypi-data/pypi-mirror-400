
from __future__ import annotations

import asyncio
import inspect
import json
import time
from dataclasses import dataclass
from http import HTTPStatus
from typing import Any, Awaitable, Callable, Iterable, Optional, TypeVar, get_type_hints

import logging
import random

import httpx
from pydantic import TypeAdapter, ValidationError as PydanticValidationError

from .client import AuthenticatedClient, Client
from .exceptions import ClientValidationError, LatticeError, map_error
from .types import Response

T = TypeVar("T")


@dataclass
class RetryConfig:
    max_retries: int = 3
    min_delay_seconds: float = 0.2
    max_delay_seconds: float = 2.0
    retry_statuses: Iterable[int] = (429, 500, 502, 503, 504)
    retry_exceptions: tuple[type[Exception], ...] = (httpx.TransportError,)


class LatticeClient:
    def __init__(
        self,
        *,
        base_url: str = "https://api.lattice.market",
        tenant_id: str,
        api_key: Optional[str] = None,
        token: Optional[str] = None,
        timeout: Optional[float] = 30.0,
        retry: Optional[RetryConfig] = None,
        validate: bool = True,
        logger: Optional[logging.Logger] = None,
        httpx_args: Optional[dict[str, Any]] = None,
        extra_headers: Optional[dict[str, str]] = None,
    ) -> None:
        headers: dict[str, str] = {"x-tenant-id": tenant_id}
        if api_key:
            headers["x-api-key"] = api_key
        if extra_headers:
            headers.update(extra_headers)

        self._tenant_id = tenant_id
        self._retry = retry or RetryConfig()
        self._validate_params = validate
        self._logger = logger
        client_args = {
            "base_url": base_url,
            "headers": headers,
            "timeout": httpx.Timeout(timeout) if timeout else None,
            "httpx_args": httpx_args or {},
        }

        if token:
            self._client: Client | AuthenticatedClient = AuthenticatedClient(
                token=token,
                **client_args,
            )
        else:
            self._client = Client(**client_args)

    @property
    def client(self) -> Client | AuthenticatedClient:
        return self._client

    def call(self, func: Callable[..., Response[T]], **kwargs: Any) -> T | None:
        response = self.call_detailed(func, **kwargs)
        if response.parsed is None:
            if int(response.status_code) in (HTTPStatus.NO_CONTENT, HTTPStatus.ACCEPTED) or not response.content:
                return None
            raise self._error_from_response(response)
        return response.parsed

    def call_detailed(self, func: Callable[..., Response[T]], **kwargs: Any) -> Response[T]:
        params = self._inject_defaults(func, kwargs)
        self._validate_parameters(func, params)
        response = self._call_with_retry(func, params)
        self._raise_for_status(response)
        return response  # pragma: no cover

    async def call_async(self, func: Callable[..., Awaitable[Response[T]]], **kwargs: Any) -> T | None:
        response = await self.call_async_detailed(func, **kwargs)
        if response.parsed is None:
            if int(response.status_code) in (HTTPStatus.NO_CONTENT, HTTPStatus.ACCEPTED) or not response.content:
                return None
            raise self._error_from_response(response)
        return response.parsed

    async def call_async_detailed(self, func: Callable[..., Awaitable[Response[T]]], **kwargs: Any) -> Response[T]:
        params = self._inject_defaults(func, kwargs)
        self._validate_parameters(func, params)
        response = await self._call_with_retry_async(func, params)
        self._raise_for_status(response)
        return response  # pragma: no cover

    def _inject_defaults(self, func: Callable[..., Any], kwargs: dict[str, Any]) -> dict[str, Any]:
        params = dict(kwargs)
        signature = inspect.signature(func)
        if "x_tenant_id" in signature.parameters and "x_tenant_id" not in params:
            params["x_tenant_id"] = self._tenant_id
        return params

    def _validate_parameters(self, func: Callable[..., Any], params: dict[str, Any]) -> None:
        if not self._validate_params:
            return
        hints = get_type_hints(func)
        for name, value in params.items():
            expected_type = hints.get(name)
            if expected_type is None:
                continue
            try:
                adapter = TypeAdapter(expected_type, config={"arbitrary_types_allowed": True})
                adapter.validate_python(value)
            except PydanticValidationError as exc:
                raise ClientValidationError(
                    message="Client-side validation failed",
                    code="CLIENT_VALIDATION_ERROR",
                    status_code=0,
                    details={"field": name, "errors": exc.errors()},
                ) from exc

    def _call_with_retry(self, func: Callable[..., Response[T]], params: dict[str, Any]) -> Response[T]:
        operation = self._operation_name(func)
        for attempt in range(self._retry.max_retries + 1):
            start = time.monotonic()
            self._log_request(operation, attempt, params)
            try:
                response = func(client=self._client, **params)
            except self._retry.retry_exceptions as exc:
                self._log_exception(operation, attempt, exc)
                if attempt >= self._retry.max_retries:
                    raise
                time.sleep(self._backoff(attempt))
                continue
            self._log_response(operation, attempt, response, start)
            if not self._should_retry(response.status_code, attempt):
                return response
            self._log_retry(operation, attempt, response.status_code)
            time.sleep(self._backoff(attempt))
        return response

    async def _call_with_retry_async(
        self, func: Callable[..., Awaitable[Response[T]]], params: dict[str, Any]
    ) -> Response[T]:
        operation = self._operation_name(func)
        for attempt in range(self._retry.max_retries + 1):
            start = time.monotonic()
            self._log_request(operation, attempt, params)
            try:
                response = await func(client=self._client, **params)
            except self._retry.retry_exceptions as exc:
                self._log_exception(operation, attempt, exc)
                if attempt >= self._retry.max_retries:
                    raise
                await asyncio.sleep(self._backoff(attempt))
                continue
            self._log_response(operation, attempt, response, start)
            if not self._should_retry(response.status_code, attempt):
                return response
            self._log_retry(operation, attempt, response.status_code)
            await asyncio.sleep(self._backoff(attempt))
        return response

    def _should_retry(self, status_code: HTTPStatus, attempt: int) -> bool:
        if attempt >= self._retry.max_retries:
            return False
        return int(status_code) in set(self._retry.retry_statuses)

    def _backoff(self, attempt: int) -> float:
        delay = min(self._retry.max_delay_seconds, self._retry.min_delay_seconds * (2 ** attempt))
        jitter = random.uniform(0, self._retry.min_delay_seconds)
        return delay + jitter

    def _operation_name(self, func: Callable[..., Any]) -> str:
        return f"{func.__module__}.{func.__name__}"

    def _log_request(self, operation: str, attempt: int, params: dict[str, Any]) -> None:
        if not self._logger:
            return
        self._logger.info(
            "lattice.request",
            extra={
                "lattice": {
                    "operation": operation,
                    "attempt": attempt,
                    "tenant_id": self._tenant_id,
                    "params": list(params.keys()),
                }
            },
        )

    def _log_response(self, operation: str, attempt: int, response: Response[Any], start_time: float) -> None:
        if not self._logger:
            return
        duration_ms = (time.monotonic() - start_time) * 1000
        self._logger.info(
            "lattice.response",
            extra={
                "lattice": {
                    "operation": operation,
                    "attempt": attempt,
                    "status_code": int(response.status_code),
                    "duration_ms": round(duration_ms, 2),
                }
            },
        )

    def _log_retry(self, operation: str, attempt: int, status_code: HTTPStatus) -> None:
        if not self._logger:
            return
        self._logger.warning(
            "lattice.retry",
            extra={
                "lattice": {
                    "operation": operation,
                    "attempt": attempt,
                    "status_code": int(status_code),
                }
            },
        )

    def _log_exception(self, operation: str, attempt: int, exc: Exception) -> None:
        if not self._logger:
            return
        self._logger.warning(
            "lattice.exception",
            extra={
                "lattice": {
                    "operation": operation,
                    "attempt": attempt,
                    "error": exc.__class__.__name__,
                }
            },
        )

    def _raise_for_status(self, response: Response[Any]) -> None:
        if int(response.status_code) < 400:
            return
        raise self._error_from_response(response)

    def _error_from_response(self, response: Response[Any]) -> LatticeError:
        message = "Request failed"
        code = "UNKNOWN_ERROR"
        details: Any = None
        retry_after = None

        try:
            payload = json.loads(response.content.decode("utf-8"))
            message = payload.get("error", message)
            code = payload.get("code", code)
            details = payload.get("details")
        except Exception:
            message = response.content.decode("utf-8", errors="ignore") or message

        retry_after_header = response.headers.get("retry-after")
        if retry_after_header and retry_after_header.isdigit():
            retry_after = int(retry_after_header)

        return map_error(message, code, int(response.status_code), details, retry_after)


class AsyncLatticeClient(LatticeClient):
    async def __aenter__(self) -> "AsyncLatticeClient":
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.client.__aexit__(exc_type, exc, tb)
