from __future__ import annotations

from typing import Any, Optional


class FinLensError(Exception):
    """Base exception for all FinLens client errors."""


class ConfigurationError(FinLensError):
    """Raised when the client is misconfigured."""


class HttpError(FinLensError):
    """Raised when an HTTP call returns an unexpected status code."""

    def __init__(self, message: str, *, status_code: Optional[int] = None, payload: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class ApiKeyValidationError(FinLensError):
    """Raised when the backend rejects or cannot validate the API key."""


class DataDecodingError(FinLensError):
    """Raised when raw API data cannot be transformed into the expected format."""
