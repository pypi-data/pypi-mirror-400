"""
Ethos Network Python SDK

The unofficial Python client for interacting with the Ethos Network API.

Usage:
    from ethos import Ethos

    client = Ethos()
    profile = client.profiles.get_by_twitter("vitalikbuterin")
    vouches = client.vouches.list(target_profile_id=profile.id)
"""

from __future__ import annotations

from ethos._client import AsyncEthos, Ethos
from ethos._config import EthosConfig
from ethos.exceptions import (
    EthosAPIError,
    EthosAuthenticationError,
    EthosError,
    EthosNotFoundError,
    EthosRateLimitError,
    EthosValidationError,
)
from ethos.types import (
    Activity,
    CategoryRank,
    ContributionDay,
    ContributionHistory,
    Endorsement,
    EndorsementSummary,
    Invitation,
    Market,
    Notification,
    NotificationSettings,
    NotificationStats,
    Profile,
    Reply,
    Review,
    Score,
    User,
    Vote,
    VoteStats,
    Vouch,
    XPDecision,
    XPHistoryEntry,
    XPSeason,
    XPTip,
    XPTipStats,
    XPValidator,
)

__version__ = "0.2.0"
__all__ = [
    # Client
    "Ethos",
    "AsyncEthos",
    "EthosConfig",
    # Core types
    "Profile",
    "Vouch",
    "Review",
    "Market",
    "Activity",
    "Score",
    # Extended types
    "User",
    "CategoryRank",
    "Endorsement",
    "EndorsementSummary",
    "Vote",
    "VoteStats",
    "Reply",
    "XPHistoryEntry",
    "XPSeason",
    "XPTip",
    "XPTipStats",
    "XPDecision",
    "XPValidator",
    "Invitation",
    "Notification",
    "NotificationStats",
    "NotificationSettings",
    "ContributionDay",
    "ContributionHistory",
    # Exceptions
    "EthosError",
    "EthosAPIError",
    "EthosNotFoundError",
    "EthosRateLimitError",
    "EthosValidationError",
    "EthosAuthenticationError",
]
