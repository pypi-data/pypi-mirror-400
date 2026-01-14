"""
Notifications resource for Ethos API.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any

from ethos.resources.base import AsyncBaseResource, BaseResource
from ethos.types.notification import (
    Notification,
    NotificationSettings,
    NotificationStats,
)

if TYPE_CHECKING:
    pass


class Notifications(BaseResource[Notification]):
    """
    Notifications API resource.

    Access and manage user notifications. Requires authentication.
    """

    _path = "/notifications"
    _model = Notification

    def list(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> Iterator[Notification]:
        """
        Get notifications for the authenticated user.

        Args:
            limit: Maximum notifications (max 50)
            offset: Pagination offset

        Yields:
            Notification objects
        """
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        yield from self._paginate(f"{self._path}/me", params=params, limit=limit)

    def get_all(self, limit: int = 50) -> list[Notification]:
        """
        Get all notifications as a list.

        Args:
            limit: Maximum notifications

        Returns:
            List of notifications
        """
        return list(self.list(limit=limit))

    def get_stats(self) -> NotificationStats:
        """
        Get notification statistics.

        Returns:
            Notification statistics including unread count
        """
        response = self._http.get(f"{self._path}/stats/me")
        return NotificationStats.model_validate(response)

    def get_unread_count(self) -> int:
        """
        Get the count of unread notifications.

        Returns:
            Number of unread notifications
        """
        stats = self.get_stats()
        return stats.unread_count

    def mark_all_read(self) -> int:
        """
        Mark all notifications as read.

        Returns:
            Number of notifications marked as read
        """
        response = self._http.post(f"{self._path}/me/mark-as-read", json={})
        return response.get("read", 0)

    def get_settings(self) -> NotificationSettings:
        """
        Get notification settings.

        Returns:
            Current notification settings
        """
        response = self._http.get(f"{self._path}/me/settings")
        return NotificationSettings.model_validate(response)

    def update_settings(self, settings: dict[str, Any]) -> NotificationSettings:
        """
        Update notification settings.

        Args:
            settings: Dictionary of notification type settings

        Returns:
            Updated notification settings
        """
        response = self._http.put(f"{self._path}/me/settings", json={"settings": settings})
        return NotificationSettings.model_validate(response)


class AsyncNotifications(AsyncBaseResource[Notification]):
    """Async Notifications API resource."""

    _path = "/notifications"
    _model = Notification

    async def list(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> AsyncIterator[Notification]:
        """Get notifications for the authenticated user."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        async for notification in self._paginate(f"{self._path}/me", params=params, limit=limit):
            yield notification

    async def get_all(self, limit: int = 50) -> list[Notification]:
        """Get all notifications as a list."""
        notifications = []
        async for notification in self.list(limit=limit):
            notifications.append(notification)
        return notifications

    async def get_stats(self) -> NotificationStats:
        """Get notification statistics."""
        response = await self._http.get(f"{self._path}/stats/me")
        return NotificationStats.model_validate(response)

    async def get_unread_count(self) -> int:
        """Get the count of unread notifications."""
        stats = await self.get_stats()
        return stats.unread_count

    async def mark_all_read(self) -> int:
        """Mark all notifications as read."""
        response = await self._http.post(f"{self._path}/me/mark-as-read", json={})
        return response.get("read", 0)

    async def get_settings(self) -> NotificationSettings:
        """Get notification settings."""
        response = await self._http.get(f"{self._path}/me/settings")
        return NotificationSettings.model_validate(response)

    async def update_settings(self, settings: dict[str, Any]) -> NotificationSettings:
        """Update notification settings."""
        response = await self._http.put(f"{self._path}/me/settings", json={"settings": settings})
        return NotificationSettings.model_validate(response)
