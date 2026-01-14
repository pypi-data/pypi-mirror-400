"""
SigninID SDK type definitions.

This module provides dataclasses and type aliases for all API request
and response types. Using dataclasses provides:
- Immutability with frozen=True
- Automatic __repr__ and __eq__
- IDE autocompletion and type checking
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterator, Literal, TypedDict


# ============================================================================
# Literals
# ============================================================================

SpamVerdict = Literal["PASS", "FAIL", "GRAY"] | None
SecurityVerdict = Literal["PASS", "FAIL", "GRAY", "PROCESSING_FAILED"] | None


# ============================================================================
# Configuration Types
# ============================================================================

class ClientOptions(TypedDict, total=False):
    """
    Client initialization options.

    All fields are optional with sensible defaults.
    """
    secret_key: str | None
    base_url: str | None
    timeout: int


class LatestEmailParams(TypedDict, total=False):
    """
    Query parameters for latest endpoint.

    Supports 'to' and 'after' filters.
    """
    to: str
    after: datetime | str


class ListEmailsParams(TypedDict, total=False):
    """
    Query parameters for list endpoints (page-based pagination).

    All parameters are optional filters.
    """
    page: int
    per_page: int
    from_: str
    to: str
    subject: str
    before: datetime | str
    after: datetime | str


# ============================================================================
# Response Models
# ============================================================================

@dataclass(frozen=True, slots=True)
class SpamRule:
    """
    Individual spam rule that triggered during analysis.

    Attributes:
        name: Rule identifier (e.g., "MISSING_HEADERS", "HTML_MESSAGE")
        score: Points added to spam score (can be negative)
        description: Human-readable rule description
    """
    name: str
    score: float
    description: str | None = None


@dataclass(frozen=True, slots=True)
class SpamRules:
    """
    Aggregated spam rules from multiple analyzers.

    Attributes:
        simple: Rules from simple spam filter
        rspamd: Rules from rspamd analyzer
    """
    simple: tuple[SpamRule, ...] = field(default_factory=tuple)
    rspamd: tuple[SpamRule, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class InboxEmail:
    """
    Received email in the inbox (without server_id).

    Contains full email metadata, spam analysis results,
    security verdicts from AWS SES, and email content.
    Returned by latest() and get() methods.
    """
    # Core identifier
    email_id: str
    message_id: str | None

    # Addresses
    from_address: str
    from_name: str | None
    to_addresses: tuple[str, ...]
    cc_addresses: tuple[str, ...] | None

    # Metadata
    subject: str | None
    received_at: datetime
    has_attachments: bool
    attachment_count: int

    # Spam analysis
    spam_score: float | None
    spam_verdict: SpamVerdict
    spam_rules: SpamRules | None

    # AWS SES verdicts
    virus_verdict: SecurityVerdict
    spf_verdict: SecurityVerdict
    dkim_verdict: SecurityVerdict
    dmarc_verdict: SecurityVerdict

    # Content
    detected_otp: str | None
    html_body: str | None
    text_body: str | None


@dataclass(frozen=True, slots=True)
class SentEmail:
    """
    Sent email record (without server_id).

    Similar to InboxEmail but includes bcc_addresses and
    uses sent_at instead of received_at. Does not include
    AWS SES security verdicts or detailed spam rules.
    Returned by latest() and get() methods.
    """
    # Core identifier
    email_id: str
    message_id: str | None

    # Addresses
    from_address: str
    from_name: str | None
    to_addresses: tuple[str, ...]
    cc_addresses: tuple[str, ...] | None
    bcc_addresses: tuple[str, ...] | None

    # Metadata
    subject: str | None
    sent_at: datetime
    has_attachments: bool
    attachment_count: int

    # Spam analysis
    spam_score: float | None
    spam_verdict: SpamVerdict

    # Content
    detected_otp: str | None
    html_body: str | None
    text_body: str | None


@dataclass(frozen=True, slots=True)
class Pagination:
    """
    Page-based pagination metadata for list responses.

    Attributes:
        page: Current page number (1-based)
        per_page: Items per page
        returned: Actual number of items returned
        has_more: Whether more items exist beyond this page
    """
    page: int
    per_page: int
    returned: int
    has_more: bool


@dataclass(frozen=True, slots=True)
class ListIdsResponse:
    """
    List response returning only email IDs.

    Use get() method to fetch full email details for each ID.

    Attributes:
        data: List of email IDs
        pagination: Pagination metadata
    """
    data: tuple[str, ...]
    pagination: Pagination

    def __iter__(self) -> Iterator[str]:
        """Allow direct iteration over email IDs."""
        return iter(self.data)

    def __len__(self) -> int:
        """Return number of email IDs."""
        return len(self.data)

    def __getitem__(self, index: int) -> str:
        """Allow indexing into email IDs."""
        return self.data[index]


# ============================================================================
# Internal API Response Types (for parsing)
# ============================================================================

class _ApiErrorDetail(TypedDict, total=False):
    """Internal: API error detail structure."""
    code: str
    message: str
    details: dict | list | None


class _ApiErrorResponse(TypedDict):
    """Internal: API error response structure."""
    error: _ApiErrorDetail
