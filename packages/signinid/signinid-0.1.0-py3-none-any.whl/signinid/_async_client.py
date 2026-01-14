"""
Asynchronous SigninID client.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from .errors import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    SigninIDError,
    TimeoutError,
    ValidationError,
)
from .resources.inbox import AsyncInboxResource
from .resources.sent import AsyncSentResource
from .types import _ApiErrorResponse

# Default API base URL
_DEFAULT_BASE_URL = "https://api.signinid.com"

# SDK version for User-Agent
_VERSION = "0.1.0"


class AsyncSigninID:
    """
    Asynchronous SigninID API client.

    Provides async access to inbox and sent email resources for testing
    email functionality in your applications.

    Args:
        secret_key: Your secret key (must start with 'sk_live_'). If not provided,
            reads from SIGNINID_SECRET_KEY environment variable.
        timeout: Request timeout in milliseconds (default: 30000)

    Attributes:
        inbox: Access inbox email operations
        sent: Access sent email operations

    Example:
        >>> import asyncio
        >>> from signinid import AsyncSigninID
        >>>
        >>> async def main():
        ...     async with AsyncSigninID(secret_key="sk_live_your_secret_key") as client:
        ...         email = await client.inbox.latest()
        ...         if email:
        ...             print(f"OTP: {email.detected_otp}")
        >>>
        >>> asyncio.run(main())

    Note:
        Always use as a context manager or call aclose() when done.
    """

    def __init__(
        self,
        *,
        secret_key: str | None = None,
        base_url: str | None = None,
        timeout: int = 30000,
    ) -> None:
        # Resolve secret key from parameter or environment variable
        resolved_secret_key = secret_key or os.environ.get("SIGNINID_SECRET_KEY")

        if not resolved_secret_key:
            raise AuthenticationError(
                "Secret key is required. Provide it in options or set "
                "SIGNINID_SECRET_KEY environment variable."
            )

        if not resolved_secret_key.startswith("sk_live_"):
            raise AuthenticationError(
                "Invalid secret key format. Secret key must start with 'sk_live_'"
            )

        self._secret_key = resolved_secret_key
        resolved_base_url = base_url or os.environ.get("SIGNINID_BASE_URL")
        self._base_url = resolved_base_url.rstrip("/") if resolved_base_url else _DEFAULT_BASE_URL
        self._timeout = timeout

        # Initialize HTTP client (convert ms to seconds for httpx)
        self._http_client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=timeout / 1000,
            headers={
                "Authorization": f"Bearer {self._secret_key}",
                "Content-Type": "application/json",
                "User-Agent": f"signinid-python/{_VERSION}",
            },
        )

        # Initialize resources
        self.inbox = AsyncInboxResource(self)
        self.sent = AsyncSentResource(self)

    async def _request(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Make an async API request (internal use).

        Args:
            path: API endpoint path
            params: Query parameters

        Returns:
            Parsed JSON response

        Raises:
            AuthenticationError: If API key is invalid
            ValidationError: If parameters are invalid
            RateLimitError: If rate limit exceeded
            NetworkError: If connection fails
            TimeoutError: If request times out
            SigninIDError: For other API errors
        """
        try:
            response = await self._http_client.get(path, params=params)
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {e}") from e
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {e}") from e
        except httpx.HTTPError as e:
            raise NetworkError(f"HTTP error: {e}") from e

        # Parse response
        try:
            body = response.json()
        except ValueError as e:
            raise SigninIDError(
                code="INVALID_RESPONSE",
                message=f"Invalid JSON response: {e}",
                status=response.status_code,
            ) from e

        # Handle errors
        if not response.is_success:
            self._handle_error_response(response.status_code, body)

        return body

    def _handle_error_response(
        self,
        status_code: int,
        body: dict[str, Any],
    ) -> None:
        """Handle API error response and raise appropriate exception."""
        error_data: _ApiErrorResponse = body
        error = error_data.get("error", {})
        code = error.get("code", "UNKNOWN_ERROR")
        message = error.get("message", "An unknown error occurred")
        details = error.get("details")

        match status_code:
            case 401:
                raise AuthenticationError(message)
            case 400:
                raise ValidationError(message, details)
            case 429:
                retry_after = None
                if isinstance(details, dict):
                    retry_after = details.get("retry_after")
                raise RateLimitError(message, retry_after)
            case _:
                raise SigninIDError(code, message, status_code)

    async def aclose(self) -> None:
        """
        Close the async HTTP client.

        Call this method when you're done using the client to release
        resources. Alternatively, use the client as an async context manager.
        """
        await self._http_client.aclose()

    async def __aenter__(self) -> AsyncSigninID:
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context manager and close client."""
        await self.aclose()

    def __repr__(self) -> str:
        return f"AsyncSigninID(base_url={self._base_url!r})"
