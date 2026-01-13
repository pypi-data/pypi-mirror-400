"""Utility MCP tools."""

import json

from fastmcp import FastMCP

from ..utils.logger import get_logger
from .dependencies import get_search_provider

logger = get_logger(__name__)


def register_utility_tools(mcp: FastMCP) -> None:
    """
    Register all utility tools with the MCP server.

    Args:
        mcp: FastMCP server instance
    """

    @mcp.tool()
    async def validate_provider() -> str:
        """
        Validate that the YouTube search provider is working correctly.

        Returns:
            JSON with validation status and provider information

        Example:
            validate_provider()
        """
        try:
            provider = get_search_provider()
            is_valid = await provider.validate_connection()

            return json.dumps(
                {
                    "valid": is_valid,
                    "provider": "yt-dlp",
                    "status": "operational" if is_valid else "error",
                },
                indent=2,
            )
        except Exception as e:
            logger.error(f"Provider validation failed: {e}")
            return json.dumps(
                {"valid": False, "provider": "yt-dlp", "status": "error", "error": str(e)}, indent=2
            )
