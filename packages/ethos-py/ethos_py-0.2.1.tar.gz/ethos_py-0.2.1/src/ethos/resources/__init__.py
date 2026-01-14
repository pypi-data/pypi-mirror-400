"""
Ethos SDK Resources

API resource classes for interacting with different endpoints.
"""

from __future__ import annotations

from ethos.resources.activities import Activities, AsyncActivities
from ethos.resources.base import AsyncBaseResource, BaseResource
from ethos.resources.contributions import AsyncContributions, Contributions
from ethos.resources.endorsements import AsyncEndorsements, Endorsements
from ethos.resources.invitations import AsyncInvitations, Invitations
from ethos.resources.markets import AsyncMarkets, Markets
from ethos.resources.notifications import AsyncNotifications, Notifications
from ethos.resources.profiles import AsyncProfiles, Profiles
from ethos.resources.replies import AsyncReplies, Replies
from ethos.resources.reviews import AsyncReviews, Reviews
from ethos.resources.scores import AsyncScores, Scores
from ethos.resources.users import AsyncUsers, Users
from ethos.resources.votes import AsyncVotes, Votes
from ethos.resources.vouches import AsyncVouches, Vouches
from ethos.resources.xp import XP, AsyncXP

__all__ = [
    # Base
    "BaseResource",
    "AsyncBaseResource",
    # Core resources
    "Profiles",
    "AsyncProfiles",
    "Vouches",
    "AsyncVouches",
    "Reviews",
    "AsyncReviews",
    "Markets",
    "AsyncMarkets",
    "Activities",
    "AsyncActivities",
    "Scores",
    "AsyncScores",
    # New resources
    "Users",
    "AsyncUsers",
    "Endorsements",
    "AsyncEndorsements",
    "Votes",
    "AsyncVotes",
    "Replies",
    "AsyncReplies",
    "XP",
    "AsyncXP",
    "Invitations",
    "AsyncInvitations",
    "Notifications",
    "AsyncNotifications",
    "Contributions",
    "AsyncContributions",
]
