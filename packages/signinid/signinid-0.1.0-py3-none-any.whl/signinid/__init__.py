"""
SigninID Python SDK

A modern Python SDK for the SigninID sandbox email testing API.

Basic usage:
    >>> from signinid import SigninID
    >>>
    >>> client = SigninID(secret_key="sk_live_your_api_key")
    >>> email = client.inbox.latest()
    >>> if email:
    ...     print(f"Detected OTP: {email.detected_otp}")

Async usage:
    >>> import asyncio
    >>> from signinid import AsyncSigninID
    >>>
    >>> async def main():
    ...     async with AsyncSigninID(secret_key="sk_live_your_api_key") as client:
    ...         email = await client.inbox.latest()
    ...         if email:
    ...             print(f"OTP: {email.detected_otp}")
    >>>
    >>> asyncio.run(main())
"""

from ._async_client import AsyncSigninID
from ._client import SigninID
from .errors import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    SigninIDError,
    TimeoutError,
    ValidationError,
)
from .types import (
    ClientOptions,
    InboxEmail,
    LatestEmailParams,
    ListEmailsParams,
    ListIdsResponse,
    Pagination,
    SecurityVerdict,
    SentEmail,
    SpamRule,
    SpamRules,
    SpamVerdict,
)
from .resources.inbox import AsyncInboxResource, InboxResource
from .resources.sent import AsyncSentResource, SentResource

__version__ = "0.1.0"

__all__ = [
    # Clients
    "SigninID",
    "AsyncSigninID",
    # Errors
    "SigninIDError",
    "AuthenticationError",
    "ValidationError",
    "NetworkError",
    "TimeoutError",
    "RateLimitError",
    # Types
    "ClientOptions",
    "LatestEmailParams",
    "ListEmailsParams",
    "InboxEmail",
    "SentEmail",
    "ListIdsResponse",
    "Pagination",
    "SpamRule",
    "SpamRules",
    "SpamVerdict",
    "SecurityVerdict",
    # Resources (for advanced usage)
    "InboxResource",
    "AsyncInboxResource",
    "SentResource",
    "AsyncSentResource",
]
