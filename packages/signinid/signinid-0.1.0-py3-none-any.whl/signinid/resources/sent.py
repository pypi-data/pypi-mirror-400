"""
Sent resource for retrieving sent emails.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from urllib.parse import quote

from ..types import ListEmailsParams, ListIdsResponse, SentEmail
from ._base import BaseResource

if TYPE_CHECKING:
    from .._async_client import AsyncSigninID
    from .._client import SigninID


class SentResource(BaseResource):
    """
    Sent email operations (synchronous).

    Access emails sent through your SigninID SMTP server with filtering
    and pagination support.

    Example:
        >>> client = SigninID("sk_live_...")
        >>> email = client.sent.latest(to="user@test.com")
        >>> if email:
        ...     print(f"Spam score: {email.spam_score}")
    """

    _client: SigninID

    def latest(
        self,
        *,
        to: str | None = None,
    ) -> SentEmail | None:
        """
        Get the most recent sent email.

        Args:
            to: Filter by recipient email address (partial match)

        Returns:
            The latest sent email, or None if no email exists.

        Raises:
            AuthenticationError: If API key is invalid
            NetworkError: If connection fails
            TimeoutError: If request times out

        Example:
            >>> email = client.sent.latest()
            >>> if email:
            ...     print(f"Spam score: {email.spam_score}")

            >>> # Filter by recipient
            >>> email = client.sent.latest(to="user@test.com")
        """
        params = {"to": to} if to else None
        response = self._client._request("/api/v1/sent/latest", params=params)
        if response is None:
            return None
        return self._parse_sent_email(response)

    def get(self, email_id: str) -> SentEmail:
        """
        Get a single sent email by ID.

        Args:
            email_id: The email ID to retrieve

        Returns:
            The sent email.

        Raises:
            SigninIDError: If email not found (404)
            ValidationError: If email_id format is invalid
            AuthenticationError: If API key is invalid

        Example:
            >>> email = client.sent.get("550e8400-e29b-41d4-a716-446655440000")
            >>> print(f"Subject: {email.subject}")
        """
        response = self._client._request(f"/api/v1/sent/{quote(email_id)}")
        return self._parse_sent_email(response)

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
        List sent email IDs with pagination.

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
            >>> response = client.sent.list()
            >>> for email_id in response:
            ...     email = client.sent.get(email_id)
            ...     print(email.subject)

            >>> # Paginate through results
            >>> response = client.sent.list(page=2, per_page=20)
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
            "/api/v1/sent",
            params=self._serialize_params(params),
        )
        return self._parse_list_ids_response(response)


class AsyncSentResource(BaseResource):
    """
    Sent email operations (asynchronous).

    Async version of SentResource for use with asyncio.

    Example:
        >>> async with AsyncSigninID("sk_live_...") as client:
        ...     email = await client.sent.latest(to="user@test.com")
        ...     if email:
        ...         print(f"Spam score: {email.spam_score}")
    """

    _client: AsyncSigninID

    async def latest(
        self,
        *,
        to: str | None = None,
    ) -> SentEmail | None:
        """
        Get the most recent sent email asynchronously.

        See SentResource.latest for full documentation.
        """
        params = {"to": to} if to else None
        response = await self._client._request("/api/v1/sent/latest", params=params)
        if response is None:
            return None
        return self._parse_sent_email(response)

    async def get(self, email_id: str) -> SentEmail:
        """
        Get a single sent email by ID asynchronously.

        See SentResource.get for full documentation.
        """
        response = await self._client._request(f"/api/v1/sent/{quote(email_id)}")
        return self._parse_sent_email(response)

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
        List sent email IDs asynchronously.

        See SentResource.list for full documentation.
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
            "/api/v1/sent",
            params=self._serialize_params(params),
        )
        return self._parse_list_ids_response(response)
