"""YouTube search provider implementation using yt-dlp."""

import asyncio
from typing import Any

import yt_dlp  # type: ignore[import-untyped]

from ..core.exceptions import (
    ExtractionError,
    NetworkError,
    SearchProviderError,
    VideoNotFoundError,
)
from ..core.interfaces import SearchProvider
from ..models.playlist import Playlist, PlaylistDetails
from ..models.search_params import SearchParams
from ..models.video import Video, VideoDetails
from ..utils.file_utils import get_ffmpeg_path
from ..utils.logger import get_logger
from .parsers import YtDlpDataParser
from .retry_decorator import async_retry

logger = get_logger(__name__)

# Error message patterns for classification
_NETWORK_ERROR_PATTERNS = ("unable to download", "connection", "timeout", "network")
_VIDEO_UNAVAILABLE_PATTERNS = ("video unavailable", "private video", "removed")


class YtDlpSearchProvider(SearchProvider):
    """
    yt-dlp implementation of SearchProvider.
    Follows Liskov Substitution Principle: can substitute SearchProvider.
    """

    def __init__(self, max_results_default: int = 10, timeout: int = 30, retries: int = 3) -> None:
        """
        Initialize yt-dlp search provider.

        Args:
            max_results_default: Default maximum number of search results
            timeout: Socket timeout in seconds
            retries: Number of retry attempts
        """
        self._max_results_default = max_results_default
        self._timeout = timeout
        self._retries = retries
        self._ydl_opts = self._build_ydl_options()
        self._parser = YtDlpDataParser()

    def _build_ydl_options(self) -> dict[str, Any]:
        """
        Build yt-dlp options for search operations.

        Returns:
            Dictionary of yt-dlp options
        """
        return {
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,  # Prevent progress output to stdout
            "skip_download": True,
            "ignoreerrors": False,  # We handle errors ourselves
            "socket_timeout": self._timeout,
            "ffmpeg_location": get_ffmpeg_path(),
        }

    def _is_network_error(self, error_msg: str) -> bool:
        """Check if error message indicates a network issue."""
        error_lower = error_msg.lower()
        return any(pattern in error_lower for pattern in _NETWORK_ERROR_PATTERNS)

    def _is_video_unavailable(self, error_msg: str) -> bool:
        """Check if error message indicates video is unavailable."""
        error_lower = error_msg.lower()
        return any(pattern in error_lower for pattern in _VIDEO_UNAVAILABLE_PATTERNS)

    @async_retry(max_attempts=3, exceptions=(NetworkError,))
    async def search(self, params: SearchParams) -> list[Video]:
        """
        Search YouTube using yt-dlp's ytsearch feature.

        Args:
            params: Search parameters

        Returns:
            List of video results

        Raises:
            InvalidQueryError: If query is invalid
            NetworkError: If network operation fails
            SearchProviderError: For other search failures
        """
        try:
            logger.info(f"Searching for: {params.query} (max_results={params.max_results})")

            # Run yt-dlp in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, self._execute_search, params)

            videos = [self._parser.parse_video(item) for item in results if item]
            logger.info(f"Found {len(videos)} videos")

            return videos

        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if self._is_network_error(error_msg):
                raise NetworkError(f"Network error during search: {error_msg}", original_error=e)
            raise SearchProviderError(f"Search failed: {error_msg}", original_error=e)
        except Exception as e:
            logger.exception(f"Unexpected error during search: {e}")
            raise SearchProviderError(f"Unexpected error during search: {str(e)}", original_error=e)

    def _execute_search(self, params: SearchParams) -> list[dict[str, Any]]:
        """
        Execute search synchronously (runs in thread pool).

        Args:
            params: Search parameters

        Returns:
            List of raw video data dictionaries
        """
        max_results = params.max_results or self._max_results_default
        search_query = f"ytsearch{max_results}:{params.query}"

        with yt_dlp.YoutubeDL(self._ydl_opts) as ydl:
            result = ydl.extract_info(search_query, download=False)
            return result.get("entries", []) if result else []

    @async_retry(max_attempts=3, exceptions=(NetworkError,))
    async def get_video_details(self, video_id: str) -> VideoDetails:
        """
        Get detailed video information.

        Args:
            video_id: YouTube video ID

        Returns:
            Detailed video information

        Raises:
            VideoNotFoundError: If video doesn't exist or is unavailable
            NetworkError: If network error occurs
            ExtractionError: If metadata extraction fails
        """
        try:
            logger.info(f"Getting details for video: {video_id}")

            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, self._execute_extract_info, video_id)

            details = self._parser.parse_video_details(info)
            logger.info(f"Retrieved details for: {details.title}")

            return details

        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if self._is_video_unavailable(error_msg):
                raise VideoNotFoundError(
                    f"Video {video_id} not found or unavailable", original_error=e
                )
            if self._is_network_error(error_msg):
                raise NetworkError(
                    f"Network error fetching video details: {error_msg}", original_error=e
                )
            raise ExtractionError(f"Failed to extract video details: {error_msg}", original_error=e)
        except Exception as e:
            logger.exception(f"Unexpected error getting video details: {e}")
            raise ExtractionError(
                f"Unexpected error getting video details: {str(e)}", original_error=e
            )

    def _execute_extract_info(self, video_id: str) -> dict[str, Any]:
        """
        Extract video info synchronously.

        Args:
            video_id: YouTube video ID

        Returns:
            Raw video information dictionary
        """
        url = f"https://www.youtube.com/watch?v={video_id}"
        with yt_dlp.YoutubeDL(self._ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info if isinstance(info, dict) else {}

    async def validate_connection(self) -> bool:
        """
        Validate yt-dlp is working correctly.

        Returns:
            True if operational, False otherwise
        """
        try:
            params = SearchParams(query="test", max_results=1, sort_by="relevance")
            await self.search(params)
            return True
        except Exception as e:
            logger.error(f"Provider validation failed: {e}")
            return False

    @async_retry(max_attempts=3, exceptions=(NetworkError,))
    async def search_playlists(self, query: str, max_results: int = 10) -> list[Playlist]:
        """
        Search YouTube for playlists matching a query.

        Args:
            query: Search query string
            max_results: Maximum number of results

        Returns:
            List of playlist results

        Raises:
            InvalidQueryError: If query is invalid
            NetworkError: If network operation fails
            SearchProviderError: For other search failures
        """
        try:
            logger.info(f"Searching playlists for: {query} (max_results={max_results})")

            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, self._execute_playlist_search, query, max_results
            )

            playlists = [self._parser.parse_playlist(item) for item in results if item]
            logger.info(f"Found {len(playlists)} playlists")

            return playlists

        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if self._is_network_error(error_msg):
                raise NetworkError(
                    f"Network error during playlist search: {error_msg}", original_error=e
                )
            raise SearchProviderError(f"Playlist search failed: {error_msg}", original_error=e)
        except Exception as e:
            logger.exception(f"Unexpected error during playlist search: {e}")
            raise SearchProviderError(
                f"Unexpected error during playlist search: {str(e)}", original_error=e
            )

    def _execute_playlist_search(self, query: str, max_results: int) -> list[dict[str, Any]]:
        """
        Execute playlist search synchronously.

        Args:
            query: Search query string
            max_results: Maximum number of results

        Returns:
            List of raw playlist data dictionaries
        """
        import urllib.parse

        # Use YouTube search URL with playlist filter
        # sp=EgIQAw%3D%3D is the URL-encoded parameter for filtering playlists only
        encoded_query = urllib.parse.quote_plus(query)
        search_url = f"https://www.youtube.com/results?search_query={encoded_query}&sp=EgIQAw%3D%3D"
        opts = self._ydl_opts.copy()
        opts["extract_flat"] = "in_playlist"  # Get playlist info without extracting all videos
        opts["playlistend"] = max_results  # Limit the number of results

        playlists = []
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                result = ydl.extract_info(search_url, download=False)

                if result:
                    entries = result.get("entries", [])
                    # Filter and collect playlist entries
                    for entry in entries:
                        if not entry:
                            continue

                        is_playlist = (
                            entry.get("_type") == "playlist"
                            or "playlist" in entry.get("ie_key", "").lower()
                            or "playlist" in entry.get("url", "").lower()
                        )

                        if is_playlist:
                            playlists.append(entry)
                            if len(playlists) >= max_results:
                                break
            except Exception as e:
                logger.warning(f"YouTube search URL failed, trying fallback method: {e}")
                # Fallback to ytsearch method
                search_query = f"ytsearch{max_results * 3}:{query}"
                result = ydl.extract_info(search_query, download=False)
                entries = result.get("entries", []) if result else []

                # Filter playlist results from mixed results
                for entry in entries:
                    if entry and entry.get("_type") == "playlist":
                        playlists.append(entry)
                        if len(playlists) >= max_results:
                            break

        return playlists

    @async_retry(max_attempts=3, exceptions=(NetworkError,))
    async def get_playlist_details(self, playlist_id: str) -> PlaylistDetails:
        """
        Get detailed information about a specific playlist.

        Args:
            playlist_id: YouTube playlist ID

        Returns:
            Detailed playlist information

        Raises:
            VideoNotFoundError: If playlist doesn't exist or is unavailable
            NetworkError: If network error occurs
            ExtractionError: If metadata extraction fails
        """
        try:
            logger.info(f"Getting details for playlist: {playlist_id}")

            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, self._execute_extract_playlist, playlist_id)

            details = self._parser.parse_playlist_details(info)
            logger.info(f"Retrieved details for playlist: {details.title}")

            return details

        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if self._is_video_unavailable(error_msg):
                raise VideoNotFoundError(
                    f"Playlist {playlist_id} not found or unavailable", original_error=e
                )
            if self._is_network_error(error_msg):
                raise NetworkError(
                    f"Network error fetching playlist details: {error_msg}", original_error=e
                )
            raise ExtractionError(
                f"Failed to extract playlist details: {error_msg}", original_error=e
            )
        except Exception as e:
            logger.exception(f"Unexpected error getting playlist details: {e}")
            raise ExtractionError(
                f"Unexpected error getting playlist details: {str(e)}", original_error=e
            )

    def _execute_extract_playlist(self, playlist_id: str) -> dict[str, Any]:
        """
        Extract playlist info synchronously.

        Args:
            playlist_id: YouTube playlist ID

        Returns:
            Raw playlist information dictionary
        """
        url = f"https://www.youtube.com/playlist?list={playlist_id}"

        opts = self._ydl_opts.copy()
        opts["extract_flat"] = "in_playlist"  # Don't extract full video info

        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info if isinstance(info, dict) else {}

    @async_retry(max_attempts=3, exceptions=(NetworkError,))
    async def get_playlist_videos(
        self, playlist_id: str, max_results: int | None = None
    ) -> list[Video]:
        """
        Get videos from a playlist.

        Args:
            playlist_id: YouTube playlist ID
            max_results: Maximum number of videos to return (None for all)

        Returns:
            List of videos in the playlist

        Raises:
            VideoNotFoundError: If playlist doesn't exist or is unavailable
            NetworkError: If network error occurs
            ExtractionError: If metadata extraction fails
        """
        try:
            logger.info(f"Getting videos from playlist: {playlist_id} (max_results={max_results})")

            loop = asyncio.get_event_loop()
            entries = await loop.run_in_executor(
                None, self._execute_extract_playlist_videos, playlist_id
            )

            # Limit results if specified
            if max_results:
                entries = entries[:max_results]

            videos = [self._parser.parse_video(entry) for entry in entries if entry]
            logger.info(f"Retrieved {len(videos)} videos from playlist")

            return videos

        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if self._is_video_unavailable(error_msg):
                raise VideoNotFoundError(
                    f"Playlist {playlist_id} not found or unavailable", original_error=e
                )
            if self._is_network_error(error_msg):
                raise NetworkError(
                    f"Network error fetching playlist videos: {error_msg}", original_error=e
                )
            raise ExtractionError(
                f"Failed to extract playlist videos: {error_msg}", original_error=e
            )
        except Exception as e:
            logger.exception(f"Unexpected error getting playlist videos: {e}")
            raise ExtractionError(
                f"Unexpected error getting playlist videos: {str(e)}", original_error=e
            )

    def _execute_extract_playlist_videos(self, playlist_id: str) -> list[dict[str, Any]]:
        """
        Extract playlist videos synchronously.

        Args:
            playlist_id: YouTube playlist ID

        Returns:
            List of raw video data dictionaries
        """
        url = f"https://www.youtube.com/playlist?list={playlist_id}"

        with yt_dlp.YoutubeDL(self._ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get("entries", []) if isinstance(info, dict) else []