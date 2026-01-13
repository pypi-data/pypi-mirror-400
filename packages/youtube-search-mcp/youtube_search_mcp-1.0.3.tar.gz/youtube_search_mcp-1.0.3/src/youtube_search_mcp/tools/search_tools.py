"""Search-related MCP tools."""

import json

from fastmcp import FastMCP

from ..core.exceptions import (
    InvalidQueryError,
    NetworkError,
    SearchProviderError,
    VideoNotFoundError,
)
from ..models.search_params import SearchParams
from ..utils.logger import get_logger
from ..utils.validators import validate_query, validate_video_id
from .dependencies import get_formatter, get_search_provider

logger = get_logger(__name__)


def register_search_tools(mcp: FastMCP) -> None:
    """
    Register all search-related tools with the MCP server.

    Args:
        mcp: FastMCP server instance
    """

    @mcp.tool(name="search_videos")
    async def search_videos(query: str, max_results: int = 10, output_format: str = "json") -> str:
        """Search YouTube for videos matching a query."""
        try:
            logger.info(f"Search request: query='{query}', max_results={max_results}")

            # Validate query
            validated_query = validate_query(query)

            # Create search parameters
            params = SearchParams(
                query=validated_query,
                max_results=max_results,
            )

            # Execute search
            provider = get_search_provider()
            videos = await provider.search(params)

            # Format results
            formatter = get_formatter(output_format)
            result = formatter.format_videos(videos)

            logger.info(f"Search completed: found {len(videos)} videos")
            return result

        except InvalidQueryError as e:
            logger.warning(f"Invalid query: {e.message}")
            return json.dumps({"error": "invalid_query", "message": e.message})
        except NetworkError as e:
            logger.error(f"Network error: {e.message}")
            return json.dumps(
                {
                    "error": "network_error",
                    "message": "Failed to connect to YouTube. Please try again.",
                    "details": e.message,
                }
            )
        except SearchProviderError as e:
            logger.error(f"Search provider error: {e.message}", exc_info=True)
            return json.dumps(
                {
                    "error": "search_failed",
                    "message": "Search operation failed. Please try a different query.",
                    "details": e.message,
                }
            )
        except Exception:
            logger.exception("Unexpected error in search_videos")
            return json.dumps(
                {
                    "error": "internal_error",
                    "message": "An unexpected error occurred. Please try again later.",
                }
            )

    @mcp.tool()
    async def get_video_info(video_id: str, output_format: str = "json") -> str:
        """
        Get detailed information about a specific YouTube video.

        Args:
            video_id: YouTube video ID (11 characters, e.g., "dQw4w9WgXcQ")
            output_format: Output format - "json" or "markdown" (default: "json")

        Returns:
            Detailed video information including description, tags, and statistics

        Example:
            get_video_info("dQw4w9WgXcQ", output_format="markdown")
        """
        try:
            logger.info(f"Get video info request: video_id='{video_id}'")

            # Validate video ID
            if not validate_video_id(video_id):
                raise InvalidQueryError(f"Invalid video ID format: {video_id}")

            # Get video details
            provider = get_search_provider()
            details = await provider.get_video_details(video_id)

            # Format results
            formatter = get_formatter(output_format)
            result = formatter.format_video_details(details)

            logger.info(f"Retrieved info for: {details.title}")
            return result

        except InvalidQueryError as e:
            logger.warning(f"Invalid video ID: {e.message}")
            return json.dumps({"error": "invalid_video_id", "message": e.message})
        except VideoNotFoundError as e:
            logger.warning(f"Video not found: {e.message}")
            return json.dumps(
                {"error": "video_not_found", "message": "Video not found or unavailable."}
            )
        except NetworkError as e:
            logger.error(f"Network error: {e.message}")
            return json.dumps(
                {
                    "error": "network_error",
                    "message": "Failed to connect to YouTube.",
                    "details": e.message,
                }
            )
        except Exception:
            logger.exception("Unexpected error in get_video_info")
            return json.dumps(
                {"error": "internal_error", "message": "An unexpected error occurred."}
            )
