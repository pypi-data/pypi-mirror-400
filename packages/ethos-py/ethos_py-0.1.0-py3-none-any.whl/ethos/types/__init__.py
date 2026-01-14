"""
Ethos SDK Types

Pydantic models for API responses.
"""

from __future__ import annotations

from ethos.types.activity import Activity
from ethos.types.contribution import ContributionDay, ContributionHistory, ForgiveResult
from ethos.types.endorsement import Endorsement, EndorsementSummary, EndorserProfile
from ethos.types.invitation import (
    Invitation,
    InvitationEligibility,
    InvitationTreeNode,
    InviterProfile,
)
from ethos.types.market import Market
from ethos.types.notification import (
    Notification,
    NotificationSettings,
    NotificationStats,
)
from ethos.types.pagination import PaginatedResponse
from ethos.types.profile import Profile
from ethos.types.reply import Reply, ReplyAuthor
from ethos.types.review import Review
from ethos.types.score import Score
from ethos.types.user import CategoryRank, User, UserStats
from ethos.types.vote import Vote, VoterProfile, VoteStats
from ethos.types.vouch import Vouch
from ethos.types.xp import (
    XPDecision,
    XPDecisionMetadata,
    XPHistoryEntry,
    XPSeason,
    XPSeasonWeek,
    XPTip,
    XPTipStats,
    XPValidator,
    XPWeeklyData,
)

__all__ = [
    # Core types
    "Profile",
    "Vouch",
    "Review",
    "Market",
    "Activity",
    "Score",
    "PaginatedResponse",
    # User types
    "User",
    "UserStats",
    "CategoryRank",
    # Endorsement types
    "Endorsement",
    "EndorsementSummary",
    "EndorserProfile",
    # Vote types
    "Vote",
    "VoteStats",
    "VoterProfile",
    # Reply types
    "Reply",
    "ReplyAuthor",
    # XP types
    "XPHistoryEntry",
    "XPWeeklyData",
    "XPSeason",
    "XPSeasonWeek",
    "XPTip",
    "XPTipStats",
    "XPDecision",
    "XPDecisionMetadata",
    "XPValidator",
    # Invitation types
    "Invitation",
    "InvitationEligibility",
    "InvitationTreeNode",
    "InviterProfile",
    # Notification types
    "Notification",
    "NotificationStats",
    "NotificationSettings",
    # Contribution types
    "ContributionDay",
    "ContributionHistory",
    "ForgiveResult",
]
