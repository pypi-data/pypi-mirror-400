"""
Ethos SDK Configuration

Configuration management for the SDK.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load .env file if present
load_dotenv()


@dataclass
class EthosConfig:
    """
    Configuration for the Ethos client.

    Attributes:
        base_url: Base URL for the Ethos API
        client_name: Name identifying your application (required by Ethos)
        timeout: Request timeout in seconds
        rate_limit: Minimum seconds between requests
        max_retries: Number of retries for failed requests
    """

    base_url: str = "https://api.ethos.network/api/v2"
    client_name: str = "ethos-py"
    timeout: float = 30.0
    rate_limit: float = 0.5
    max_retries: int = 3

    @classmethod
    def from_env(cls) -> EthosConfig:
        """Create configuration from environment variables."""
        return cls(
            base_url=os.getenv("ETHOS_API_BASE_URL", cls.base_url),
            client_name=os.getenv("ETHOS_CLIENT_NAME", cls.client_name),
            timeout=float(os.getenv("ETHOS_TIMEOUT", str(cls.timeout))),
            rate_limit=float(os.getenv("ETHOS_RATE_LIMIT", str(cls.rate_limit))),
            max_retries=int(os.getenv("ETHOS_MAX_RETRIES", str(cls.max_retries))),
        )


# Default configuration instance
DEFAULT_CONFIG = EthosConfig.from_env()
