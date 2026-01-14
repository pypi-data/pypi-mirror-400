"""
Market model for Ethos reputation markets.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Market(BaseModel):
    """
    A reputation market on Ethos Markets.

    Reputation markets allow users to trade trust/distrust votes
    on a person's reputation using an LMSR-based AMM.
    These markets are perpetual (never resolve).
    """

    id: int

    # Subject of the market
    profile_id: int = Field(..., alias="profileId")

    # Market state
    trust_votes: int = Field(0, alias="trustVotes")
    distrust_votes: int = Field(0, alias="distrustVotes")

    # Prices (0.0 to 1.0)
    trust_price: float = Field(0.5, alias="trustPrice")
    distrust_price: float = Field(0.5, alias="distrustPrice")

    # Volume
    total_volume: float = Field(0.0, alias="totalVolume")

    # Market parameters
    liquidity_parameter: float | None = Field(None, alias="liquidityParameter")

    # Status
    is_active: bool = Field(True, alias="isActive")

    # Timestamps
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

    @property
    def trust_percentage(self) -> float:
        """Get trust as a percentage (0-100)."""
        return self.trust_price * 100

    @property
    def distrust_percentage(self) -> float:
        """Get distrust as a percentage (0-100)."""
        return self.distrust_price * 100

    @property
    def market_sentiment(self) -> str:
        """
        Get overall market sentiment.

        Returns:
            "bullish" if trust > 60%
            "bearish" if distrust > 60%
            "neutral" otherwise
        """
        if self.trust_price > 0.6:
            return "bullish"
        elif self.distrust_price > 0.6:
            return "bearish"
        else:
            return "neutral"

    @property
    def is_volatile(self) -> bool:
        """Check if market is volatile (close to 50/50)."""
        return 0.4 <= self.trust_price <= 0.6
