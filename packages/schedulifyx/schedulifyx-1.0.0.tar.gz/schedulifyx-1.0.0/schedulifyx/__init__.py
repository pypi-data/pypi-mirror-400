"""
SchedulifyX SDK - Official Python SDK for SchedulifyX API
https://schedulifyx.com/docs
"""

from .client import Schedulify, SchedulifyError
from .types import (
    Post,
    Account,
    Analytics,
    AnalyticsOverview,
    Usage,
    Tenant,
    QueueSlot,
    QueueSchedule,
    MediaUploadResponse,
    PaginatedResponse,
)

__version__ = "1.0.0"
__all__ = [
    "Schedulify",
    "SchedulifyError",
    "Post",
    "Account",
    "Analytics",
    "AnalyticsOverview",
    "Usage",
    "Tenant",
    "QueueSlot",
    "QueueSchedule",
    "MediaUploadResponse",
    "PaginatedResponse",
]
