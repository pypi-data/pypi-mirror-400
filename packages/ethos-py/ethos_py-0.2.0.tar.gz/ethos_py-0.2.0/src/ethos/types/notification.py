"""
Notification types for Ethos API.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

NotificationType = Literal[
    "SIMPLE",
    "VOUCH",
    "REVIEW",
    "REPLY",
    "VOTE",
    "INVITATION",
    "XP",
    "MENTION",
    "FOLLOW",
]


class Notification(BaseModel):
    """
    A notification on Ethos Network.

    Notifications alert users to activities that involve them,
    such as receiving reviews, vouches, replies, etc.
    """

    id: int
    type: str
    title: str | None = None
    message: str | None = None
    is_read: bool = Field(False, alias="isRead")

    # Related entities
    actor_profile_id: int | None = Field(None, alias="actorProfileId")
    target_profile_id: int | None = Field(None, alias="targetProfileId")
    activity_id: int | None = Field(None, alias="activityId")
    activity_type: str | None = Field(None, alias="activityType")

    # Actor profile info
    actor: dict | None = None

    # URL to view
    url: str | None = None

    # Timestamps
    created_at: datetime | None = Field(None, alias="createdAt")

    model_config = {"populate_by_name": True, "extra": "allow"}

    @property
    def is_unread(self) -> bool:
        """Check if notification is unread."""
        return not self.is_read


class NotificationStats(BaseModel):
    """Statistics about notifications."""

    unread_count: int = Field(0, alias="unreadCount")

    model_config = {"populate_by_name": True, "extra": "allow"}


class NotificationTypeSettings(BaseModel):
    """Settings for a notification type."""

    list_disabled: bool = Field(False, alias="listDisabled")
    push_disabled: bool = Field(False, alias="pushDisabled")

    model_config = {"populate_by_name": True, "extra": "allow"}


class NotificationSettings(BaseModel):
    """User notification settings."""

    SIMPLE: NotificationTypeSettings | None = None
    VOUCH: NotificationTypeSettings | None = None
    REVIEW: NotificationTypeSettings | None = None
    REPLY: NotificationTypeSettings | None = None
    VOTE: NotificationTypeSettings | None = None
    INVITATION: NotificationTypeSettings | None = None
    XP: NotificationTypeSettings | None = None
    MENTION: NotificationTypeSettings | None = None
    FOLLOW: NotificationTypeSettings | None = None

    model_config = {"populate_by_name": True, "extra": "allow"}

    def get_settings(self, notification_type: str) -> NotificationTypeSettings | None:
        """Get settings for a specific notification type."""
        return getattr(self, notification_type.upper(), None)
