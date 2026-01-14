"""
SigninID SDK exceptions.

This module provides a hierarchy of exceptions:
- SigninIDError (base)
  - AuthenticationError (401)
  - ValidationError (400)
  - NetworkError (connection issues)
  - TimeoutError (request timeout)
  - RateLimitError (429)
"""

from __future__ import annotations

from typing import Any


class SigninIDError(Exception):
    """
    Base error class for SigninID SDK.

    All SDK-specific errors inherit from this class, making it easy to catch
    any SigninID-related error with a single except clause.

    Attributes:
        code: Machine-readable error code (e.g., "UNAUTHORIZED", "INVALID_REQUEST")
        message: Human-readable error description
        status: HTTP status code (0 for non-HTTP errors like network/timeout)
    """

    def __init__(
        self,
        code: str,
        message: str,
        status: int,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code!r}, message={self.message!r}, status={self.status})"


class AuthenticationError(SigninIDError):
    """
    Raised when API key is missing or invalid.

    This error occurs when:
    - No API key is provided
    - API key format is invalid (must start with 'sk_live_')
    - API key has been revoked or is expired
    """

    def __init__(self, message: str = "Invalid API key") -> None:
        super().__init__(code="UNAUTHORIZED", message=message, status=401)


class ValidationError(SigninIDError):
    """
    Raised when request parameters are invalid.

    This error occurs when the API rejects the request due to invalid
    query parameters, such as an out-of-range limit or malformed dates.

    Attributes:
        details: Additional validation error details from the API response
    """

    def __init__(
        self,
        message: str,
        details: Any | None = None,
    ) -> None:
        super().__init__(code="INVALID_REQUEST", message=message, status=400)
        self.details = details

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, details={self.details!r})"


class NetworkError(SigninIDError):
    """
    Raised when a network error occurs.

    This error occurs when the SDK cannot establish a connection to the
    SigninID API, such as DNS resolution failures or connection refused.
    """

    def __init__(self, message: str = "Network error occurred") -> None:
        super().__init__(code="NETWORK_ERROR", message=message, status=0)


class TimeoutError(SigninIDError):
    """
    Raised when request times out.

    This error occurs when the API request exceeds the configured timeout
    duration. The default timeout is 30 seconds.
    """

    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(code="TIMEOUT", message=message, status=0)


class RateLimitError(SigninIDError):
    """
    Raised when rate limit is exceeded.

    This error occurs when too many requests are made in a short period.
    Consider implementing exponential backoff or reducing request frequency.

    Attributes:
        retry_after: Seconds to wait before retrying (if provided by API)
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
    ) -> None:
        super().__init__(code="RATE_LIMITED", message=message, status=429)
        self.retry_after = retry_after
