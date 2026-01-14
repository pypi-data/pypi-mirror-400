"""
Base resource class for API resources.

Provides shared functionality for parameter serialization
and response parsing across Inbox and Sent resources.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..types import (
    InboxEmail,
    ListEmailsParams,
    ListIdsResponse,
    Pagination,
    SentEmail,
    SpamRule,
    SpamRules,
)

if TYPE_CHECKING:
    from .._async_client import AsyncSigninID
    from .._client import SigninID


class BaseResource:
    """Base class for API resources with shared utilities."""

    def __init__(self, client: SigninID | AsyncSigninID) -> None:
        self._client = client

    def _serialize_params(
        self,
        params: ListEmailsParams | None,
    ) -> dict[str, Any] | None:
        """
        Serialize query parameters for API request.

        Handles:
        - Python's 'from_' parameter name to API's 'from'
        - datetime to ISO format string conversion
        - Filtering out None values
        """
        if params is None:
            return None

        result: dict[str, Any] = {}

        for key, value in params.items():
            if value is None:
                continue

            # Handle Python reserved word 'from'
            api_key = "from" if key == "from_" else key

            # Convert datetime to ISO string
            if isinstance(value, datetime):
                result[api_key] = value.isoformat()
            else:
                result[api_key] = value

        return result if result else None

    @staticmethod
    def _parse_spam_rules(data: dict[str, Any] | None) -> SpamRules | None:
        """Parse spam rules from API response."""
        if data is None:
            return None

        return SpamRules(
            simple=tuple(
                SpamRule(
                    name=rule.get("name", ""),
                    score=rule.get("score", 0.0),
                    description=rule.get("description"),
                )
                for rule in data.get("simple", [])
            ),
            rspamd=tuple(
                SpamRule(
                    name=rule.get("name", ""),
                    score=rule.get("score", 0.0),
                    description=rule.get("description"),
                )
                for rule in data.get("rspamd", [])
            ),
        )

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        """Parse ISO datetime string to datetime object."""
        if value is None:
            return None
        # Handle both with and without timezone
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return datetime.fromisoformat(value)

    @staticmethod
    def _to_tuple(value: list[str] | None) -> tuple[str, ...] | None:
        """Convert list to tuple, preserving None."""
        if value is None:
            return None
        return tuple(value)

    def _parse_inbox_email(self, data: dict[str, Any]) -> InboxEmail:
        """Parse API response into InboxEmail dataclass (without server_id)."""
        received_at = self._parse_datetime(data.get("received_at"))
        if received_at is None:
            raise ValueError("received_at is required for InboxEmail")

        return InboxEmail(
            email_id=data["email_id"],
            message_id=data.get("message_id"),
            from_address=data["from_address"],
            from_name=data.get("from_name"),
            to_addresses=tuple(data.get("to_addresses", [])),
            cc_addresses=self._to_tuple(data.get("cc_addresses")),
            subject=data.get("subject"),
            received_at=received_at,
            has_attachments=data.get("has_attachments", False),
            attachment_count=data.get("attachment_count", 0),
            spam_score=data.get("spam_score"),
            spam_verdict=data.get("spam_verdict"),
            spam_rules=self._parse_spam_rules(data.get("spam_rules")),
            virus_verdict=data.get("virus_verdict"),
            spf_verdict=data.get("spf_verdict"),
            dkim_verdict=data.get("dkim_verdict"),
            dmarc_verdict=data.get("dmarc_verdict"),
            detected_otp=data.get("detected_otp"),
            html_body=data.get("html_body"),
            text_body=data.get("text_body"),
        )

    def _parse_sent_email(self, data: dict[str, Any]) -> SentEmail:
        """Parse API response into SentEmail dataclass (without server_id)."""
        sent_at = self._parse_datetime(data.get("sent_at"))
        if sent_at is None:
            raise ValueError("sent_at is required for SentEmail")

        return SentEmail(
            email_id=data["email_id"],
            message_id=data.get("message_id"),
            from_address=data["from_address"],
            from_name=data.get("from_name"),
            to_addresses=tuple(data.get("to_addresses", [])),
            cc_addresses=self._to_tuple(data.get("cc_addresses")),
            bcc_addresses=self._to_tuple(data.get("bcc_addresses")),
            subject=data.get("subject"),
            sent_at=sent_at,
            has_attachments=data.get("has_attachments", False),
            attachment_count=data.get("attachment_count", 0),
            spam_score=data.get("spam_score"),
            spam_verdict=data.get("spam_verdict"),
            detected_otp=data.get("detected_otp"),
            html_body=data.get("html_body"),
            text_body=data.get("text_body"),
        )

    def _parse_pagination(self, data: dict[str, Any]) -> Pagination:
        """Parse page-based pagination metadata from API response."""
        return Pagination(
            page=data.get("page", 1),
            per_page=data.get("per_page", 10),
            returned=data.get("returned", 0),
            has_more=data.get("has_more", False),
        )

    def _parse_list_ids_response(
        self,
        data: dict[str, Any],
    ) -> ListIdsResponse:
        """Parse list response returning only email IDs."""
        return ListIdsResponse(
            data=tuple(data.get("data", [])),
            pagination=self._parse_pagination(data.get("pagination", {})),
        )
