"""
Contribution types for Ethos API.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ContributionDay(BaseModel):
    """A single day's contribution data."""

    date: str
    tasks: int = 0
    forgiven: bool = False

    model_config = {"populate_by_name": True, "extra": "allow"}

    @property
    def has_activity(self) -> bool:
        """Check if there was activity on this day."""
        return self.tasks > 0 or self.forgiven


class ContributionHistory(BaseModel):
    """A user's contribution history."""

    history: list[ContributionDay] = Field(default_factory=list)

    model_config = {"populate_by_name": True, "extra": "allow"}

    @property
    def total_days(self) -> int:
        """Get total number of days in history."""
        return len(self.history)

    @property
    def active_days(self) -> int:
        """Get number of days with activity."""
        return sum(1 for day in self.history if day.has_activity)

    @property
    def total_tasks(self) -> int:
        """Get total number of tasks completed."""
        return sum(day.tasks for day in self.history)

    @property
    def forgiven_days(self) -> int:
        """Get number of forgiven days."""
        return sum(1 for day in self.history if day.forgiven)


class ForgiveResult(BaseModel):
    """Result of forgiving a missed contribution day."""

    ok: bool
    message: str | None = None
    forgiven_date: str | None = Field(None, alias="forgivenDate")
    updated: int = 0

    model_config = {"populate_by_name": True, "extra": "allow"}
