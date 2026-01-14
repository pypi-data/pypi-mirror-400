"""Configuration for VIKK MCP Server."""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """MCP Server configuration loaded from environment."""

    api_url: str
    api_key: str
    timeout: int

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            api_url=os.getenv("VIKK_API_URL", "http://localhost:8000"),
            api_key=os.getenv("VIKK_API_KEY", ""),
            timeout=int(os.getenv("VIKK_TIMEOUT", "60")),
        )


config = Config.from_env()
