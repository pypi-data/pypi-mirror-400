"""Type definitions for SchedulifyX SDK"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class Post:
    id: str
    content: str
    status: str  # 'draft' | 'scheduled' | 'publishing' | 'published' | 'failed'
    account_ids: List[str]
    created_at: str
    updated_at: str
    media_urls: Optional[List[str]] = None
    publish_at: Optional[str] = None
    platform_overrides: Optional[Dict[str, Dict[str, str]]] = None


@dataclass
class Account:
    id: str
    platform: str
    platform_account_id: str
    name: str
    is_active: bool
    created_at: str
    username: Optional[str] = None
    profile_picture: Optional[str] = None


@dataclass
class Analytics:
    account_id: str
    followers: int
    following: int
    posts: int
    engagement: float
    updated_at: str


@dataclass
class AnalyticsOverview:
    total_posts: int
    scheduled_posts: int
    published_posts: int
    failed_posts: int
    total_accounts: int
    active_accounts: int


@dataclass
class Usage:
    requests_today: int
    daily_limit: int
    remaining_today: int
    monthly_requests: int
    last_used_at: Optional[str]


@dataclass
class Tenant:
    id: str
    external_id: str
    created_at: str
    email: Optional[str] = None
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class QueueSlot:
    day_of_week: int  # 0-6, Sunday = 0
    time: str  # HH:MM format


@dataclass
class QueueSchedule:
    id: str
    profile_id: str
    timezone: str
    slots: List[QueueSlot]
    active: bool


@dataclass
class MediaUploadResponse:
    upload_url: str
    media_url: str
    expires_in: int


@dataclass
class PaginatedResponse:
    data: List[Any]
    total: int
    limit: int
    offset: int
    has_more: bool
