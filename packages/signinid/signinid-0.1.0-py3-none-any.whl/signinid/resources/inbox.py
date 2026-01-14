"""
Inbox resource for retrieving received emails.
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from urllib.parse import quote

from ..types import InboxEmail, ListEmailsParams, ListIdsResponse
from ._base import BaseResource

if TYPE_CHECKING:
    from .._async_client import AsyncSigninID
    from .._client import SigninID


class InboxResource(BaseResource):
    """
    Inbox email operations (synchronous).

    Access received emails in your SigninID inbox with filtering
    and pagination support.

    Example:
        >>> client = SigninID("sk_live_...")
        >>> email = client.inbox.latest(to="user@test.com")
        >>> if email:
        ...     print(f"OTP: {email.detected_otp}")
    """

    _client: SigninID

    def latest(
        self,
        *,
        to: str | None = None,
        after: datetime | str | None = None,
    ) -> InboxEmail | None:
        """
        Get the most recent inbox email.

        Args:
            to: Filter by recipient email address (partial match)
            after: Only return emails received after this timestamp (ISO 8601 or datetime)

        Returns:
            The latest inbox email, or None if no email exists.

        Raises:
            AuthenticationError: If API key is invalid
            NetworkError: If connection fails
            TimeoutError: If request times out

        Example:
            >>> email = client.inbox.latest()
            >>> if email:
            ...     print(f"OTP: {email.detected_otp}")

            >>> # Filter by recipient
            >>> email = client.inbox.latest(to="user@test.com")
        """
        params: dict[str, str] = {}
        if to:
            params["to"] = to
        if after:
            params["after"] = after.isoformat() if isinstance(after, datetime) else after
        response = self._client._request(
            "/api/v1/inbox/latest",
            params=params if params else None,
        )
        if response is None:
            return None
        return self._parse_inbox_email(response)

    def wait_for_new(
        self,
        *,
        to: str | None = None,
        timeout: int = 30,
    ) -> InboxEmail | None:
        """
        Wait for a new email to arrive.

        Polls the inbox until a new email arrives or timeout is reached.
        Useful for testing signup/login flows where you need to wait for
        a verification email.

        Args:
            to: Filter by recipient email address (partial match)
            timeout: Maximum wait time in seconds (default: 30)

        Returns:
            The new inbox email, or None if timeout is reached.

        Raises:
            AuthenticationError: If API key is invalid
            NetworkError: If connection fails

        Example:
            >>> # Wait for a new email (default 30s timeout)
            >>> email = client.inbox.wait_for_new(to="user@test.com")
            >>> if email:
            ...     print(f"OTP: {email.detected_otp}")

            >>> # Custom timeout
            >>> email = client.inbox.wait_for_new(to="user@test.com", timeout=60)
        """
        start_time = datetime.now(timezone.utc).isoformat()
        deadline = time.time() + timeout

        while time.time() < deadline:
            email = self.latest(to=to, after=start_time)
            if email is not None:
                return email
            time.sleep(1)

        return None

    def get(self, email_id: str) -> InboxEmail:
        """
        Get a single inbox email by ID.

        Args:
            email_id: The email ID to retrieve

        Returns:
            The inbox email.

        Raises:
            SigninIDError: If email not found (404)
            ValidationError: If email_id format is invalid
            AuthenticationError: If API key is invalid

        Example:
            >>> email = client.inbox.get("550e8400-e29b-41d4-a716-446655440000")
            >>> print(f"Subject: {email.subject}")
        """
        response = self._client._request(f"/api/v1/inbox/{quote(email_id)}")
        return self._parse_inbox_email(response)

    def list(
        self,
        *,
        page: int | None = None,
        per_page: int | None = None,
        from_: str | None = None,
        to: str | None = None,
        subject: str | None = None,
        before: datetime | str | None = None,
        after: datetime | str | None = None,
    ) -> ListIdsResponse:
        """
        List inbox email IDs with pagination.

        Returns only email IDs. Use get() to fetch full email details.

        Args:
            page: Page number (1, 2, 3..., default: 1)
            per_page: Results per page (1-100, default: 10)
            from_: Filter by sender email address (partial match)
            to: Filter by recipient email address (partial match)
            subject: Filter by subject (partial match)
            before: Return emails before this date (ISO 8601 or datetime)
            after: Return emails after this date (ISO 8601 or datetime)

        Returns:
            ListIdsResponse containing email IDs and pagination info.

        Raises:
            AuthenticationError: If API key is invalid
            ValidationError: If parameters are invalid
            NetworkError: If connection fails
            TimeoutError: If request times out

        Example:
            >>> # Get first page of email IDs
            >>> response = client.inbox.list()
            >>> for email_id in response:
            ...     email = client.inbox.get(email_id)
            ...     print(email.subject)

            >>> # Paginate through results
            >>> response = client.inbox.list(page=2, per_page=20)
        """
        params: ListEmailsParams = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        if from_ is not None:
            params["from_"] = from_
        if to is not None:
            params["to"] = to
        if subject is not None:
            params["subject"] = subject
        if before is not None:
            params["before"] = before
        if after is not None:
            params["after"] = after

        response = self._client._request(
            "/api/v1/inbox",
            params=self._serialize_params(params),
        )
        return self._parse_list_ids_response(response)


class AsyncInboxResource(BaseResource):
    """
    Inbox email operations (asynchronous).

    Async version of InboxResource for use with asyncio.

    Example:
        >>> async with AsyncSigninID("sk_live_...") as client:
        ...     email = await client.inbox.latest(to="user@test.com")
        ...     if email:
        ...         print(f"OTP: {email.detected_otp}")
    """

    _client: AsyncSigninID

    async def latest(
        self,
        *,
        to: str | None = None,
        after: datetime | str | None = None,
    ) -> InboxEmail | None:
        """
        Get the most recent inbox email asynchronously.

        See InboxResource.latest for full documentation.
        """
        params: dict[str, str] = {}
        if to:
            params["to"] = to
        if after:
            params["after"] = after.isoformat() if isinstance(after, datetime) else after
        response = await self._client._request(
            "/api/v1/inbox/latest",
            params=params if params else None,
        )
        if response is None:
            return None
        return self._parse_inbox_email(response)

    async def wait_for_new(
        self,
        *,
        to: str | None = None,
        timeout: int = 30,
    ) -> InboxEmail | None:
        """
        Wait for a new email to arrive asynchronously.

        See InboxResource.wait_for_new for full documentation.
        """
        start_time = datetime.now(timezone.utc).isoformat()
        deadline = time.time() + timeout

        while time.time() < deadline:
            email = await self.latest(to=to, after=start_time)
            if email is not None:
                return email
            await asyncio.sleep(1)

        return None

    async def get(self, email_id: str) -> InboxEmail:
        """
        Get a single inbox email by ID asynchronously.

        See InboxResource.get for full documentation.
        """
        response = await self._client._request(f"/api/v1/inbox/{quote(email_id)}")
        return self._parse_inbox_email(response)

    async def list(
        self,
        *,
        page: int | None = None,
        per_page: int | None = None,
        from_: str | None = None,
        to: str | None = None,
        subject: str | None = None,
        before: datetime | str | None = None,
        after: datetime | str | None = None,
    ) -> ListIdsResponse:
        """
        List inbox email IDs asynchronously.

        See InboxResource.list for full documentation.
        """
        params: ListEmailsParams = {}
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["per_page"] = per_page
        if from_ is not None:
            params["from_"] = from_
        if to is not None:
            params["to"] = to
        if subject is not None:
            params["subject"] = subject
        if before is not None:
            params["before"] = before
        if after is not None:
            params["after"] = after

        response = await self._client._request(
            "/api/v1/inbox",
            params=self._serialize_params(params),
        )
        return self._parse_list_ids_response(response)
