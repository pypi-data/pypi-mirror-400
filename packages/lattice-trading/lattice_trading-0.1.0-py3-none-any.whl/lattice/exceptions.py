
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class LatticeError(Exception):
    message: str
    code: str
    status_code: int
    details: Optional[Any] = None

    def __str__(self) -> str:
        return f"{self.code} ({self.status_code}): {self.message}"


class AuthenticationError(LatticeError):
    pass


class ForbiddenError(LatticeError):
    pass


class NotFoundError(LatticeError):
    pass


class ConflictError(LatticeError):
    pass


class RateLimitError(LatticeError):
    retry_after: Optional[int] = None

    def __init__(self, message: str, code: str, status_code: int, retry_after: Optional[int] = None, details: Any = None):
        super().__init__(message=message, code=code, status_code=status_code, details=details)
        self.retry_after = retry_after


class ValidationError(LatticeError):
    pass


class ClientValidationError(LatticeError):
    pass


def map_error(message: str, code: str, status_code: int, details: Any = None, retry_after: Optional[int] = None) -> LatticeError:
    if status_code == 401:
        return AuthenticationError(message, code, status_code, details)
    if status_code == 403:
        return ForbiddenError(message, code, status_code, details)
    if status_code == 404:
        return NotFoundError(message, code, status_code, details)
    if status_code == 409:
        return ConflictError(message, code, status_code, details)
    if status_code == 429:
        return RateLimitError(message, code, status_code, retry_after=retry_after, details=details)
    if status_code == 400:
        return ValidationError(message, code, status_code, details)
    return LatticeError(message, code, status_code, details)
