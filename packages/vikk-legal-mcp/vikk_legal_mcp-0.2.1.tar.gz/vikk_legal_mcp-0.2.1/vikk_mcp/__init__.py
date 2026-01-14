"""VIKK Legal AI MCP Server and Python Client."""

from vikk_mcp.client import VikkAPIClient, VikkAPIError, VikkAuthenticationError, VikkRateLimitError

__version__ = "0.2.1"

__all__ = [
    "VikkAPIClient",
    "VikkAPIError",
    "VikkAuthenticationError",
    "VikkRateLimitError",
]
