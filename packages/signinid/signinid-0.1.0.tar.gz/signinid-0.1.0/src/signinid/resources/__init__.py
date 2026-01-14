"""
SigninID API resources.
"""

from .inbox import AsyncInboxResource, InboxResource
from .sent import AsyncSentResource, SentResource

__all__ = [
    "InboxResource",
    "AsyncInboxResource",
    "SentResource",
    "AsyncSentResource",
]
