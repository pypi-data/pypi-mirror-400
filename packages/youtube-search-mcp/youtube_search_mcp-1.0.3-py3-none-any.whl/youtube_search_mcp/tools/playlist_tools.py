"""Playlist-related MCP tools."""

import json

from fastmcp import FastMCP

from ..core.exceptions import (
    ExtractionError,
    InvalidQueryError,
    NetworkError,
    SearchProviderError,
    VideoNotFoundError,
)
from ..utils.logger import get_logger
from ..utils.validators import validate_query
from .dependencies import get_formatter, get_search_provider

logger = get_logger(__name__)


def register_playlist_tools(mcp: FastMCP) -> None:
    """
    Register all playlist-related tools with the MCP server.

    Args:
        mcp: FastMCP server instance
    """

    @mcp.tool()
    async def search_playlists(
        query: str, max_results: int = 10, output_format: str = "json"
    ) -> str:
        """
        Search YouTube for playlists matching a query.

        Args:
            query: Search query string (e.g., "python tutorial playlist")
            max_results: Maximum number of results to return (1-50, default: 10)
            output_format: Output format - "json" or "markdown" (default: "json")

        Returns:
            Formatted search results with playlist metadata

        Example:
            search_playlists("machine learning course", max_results=5, output_format="json")
        """
        try:
            logger.info(f"Playlist search request: query='{query}', max_results={max_results}")

            # Validate query
            validated_query = validate_query(query)

            # Execute search
            provider = get_search_provider()
            playlists = await provider.search_playlists(validated_query, max_results)

            # Format results
            formatter = get_formatter(output_format)
            result = formatter.format_playlists(playlists)

            logger.info(f"Playlist search completed: found {len(playlists)} playlists")
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
                    "message": "Playlist search operation failed. Please try a different query.",
                    "details": e.message,
                }
            )
        except Exception:
            logger.exception("Unexpected error in search_playlists")
            return json.dumps(
                {
                    "error": "internal_error",
                    "message": "An unexpected error occurred. Please try again later.",
                }
            )

    @mcp.tool()
    async def get_playlist_info(playlist_id: str, output_format: str = "json") -> str:
        """
        Get detailed information about a specific YouTube playlist.

        Args:
            playlist_id: YouTube playlist ID (e.g., "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf")
            output_format: Output format - "json" or "markdown" (default: "json")

        Returns:
            Detailed playlist information including title, creator, video count, and description

        Example:
            get_playlist_info("PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf", output_format="markdown")
        """
        try:
            logger.info(f"Get playlist info request: playlist_id='{playlist_id}'")

            # Basic validation
            if not playlist_id or len(playlist_id) < 10:
                raise InvalidQueryError(f"Invalid playlist ID format: {playlist_id}")

            # Get playlist details
            provider = get_search_provider()
            details = await provider.get_playlist_details(playlist_id)

            # Format results
            formatter = get_formatter(output_format)
            result = formatter.format_playlist_details(details)

            logger.info(f"Retrieved info for playlist: {details.title}")
            return result

        except InvalidQueryError as e:
            logger.warning(f"Invalid playlist ID: {e.message}")
            return json.dumps({"error": "invalid_playlist_id", "message": e.message})
        except VideoNotFoundError as e:
            logger.warning(f"Playlist not found: {e.message}")
            return json.dumps(
                {"error": "playlist_not_found", "message": "Playlist not found or unavailable."}
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
        except ExtractionError as e:
            logger.error(f"Extraction error: {e.message}")
            return json.dumps(
                {
                    "error": "extraction_failed",
                    "message": "Failed to extract playlist information.",
                    "details": e.message,
                }
            )
        except Exception:
            logger.exception("Unexpected error in get_playlist_info")
            return json.dumps(
                {"error": "internal_error", "message": "An unexpected error occurred."}
            )

    @mcp.tool()
    async def get_playlist_videos(
        playlist_id: str, max_results: int | None = None, output_format: str = "json"
    ) -> str:
        """
        Get list of videos from a YouTube playlist.

        Args:
            playlist_id: YouTube playlist ID (e.g., "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf")
            max_results: Maximum number of videos to return (None for all videos, default: None)
            output_format: Output format - "json" or "markdown" (default: "json")

        Returns:
            List of videos in the playlist with metadata

        Example:
            get_playlist_videos("PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf", max_results=20)
        """
        try:
            logger.info(
                f"Get playlist videos request: playlist_id='{playlist_id}', max_results={max_results}"
            )

            # Basic validation
            if not playlist_id or len(playlist_id) < 10:
                raise InvalidQueryError(f"Invalid playlist ID format: {playlist_id}")

            # Get playlist videos
            provider = get_search_provider()
            videos = await provider.get_playlist_videos(playlist_id, max_results)

            # Format results
            formatter = get_formatter(output_format)
            result = formatter.format_videos(videos)

            logger.info(f"Retrieved {len(videos)} videos from playlist")
            return result

        except InvalidQueryError as e:
            logger.warning(f"Invalid playlist ID: {e.message}")
            return json.dumps({"error": "invalid_playlist_id", "message": e.message})
        except VideoNotFoundError as e:
            logger.warning(f"Playlist not found: {e.message}")
            return json.dumps(
                {"error": "playlist_not_found", "message": "Playlist not found or unavailable."}
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
        except ExtractionError as e:
            logger.error(f"Extraction error: {e.message}")
            return json.dumps(
                {
                    "error": "extraction_failed",
                    "message": "Failed to extract playlist videos.",
                    "details": e.message,
                }
            )
        except Exception:
            logger.exception("Unexpected error in get_playlist_videos")
            return json.dumps(
                {"error": "internal_error", "message": "An unexpected error occurred."}
            )
