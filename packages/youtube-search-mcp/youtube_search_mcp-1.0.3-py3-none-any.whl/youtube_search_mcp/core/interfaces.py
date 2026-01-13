"""Abstract base classes and protocols for dependency inversion."""

from abc import ABC, abstractmethod

# Forward references to avoid circular imports
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from ..models.download_params import DownloadParams, DownloadResult
    from ..models.playlist import Playlist, PlaylistDetails
    from ..models.search_params import SearchParams
    from ..models.video import Video, VideoDetails


class SearchProvider(ABC):
    """
    Abstract base class for search providers.
    Follows Open/Closed Principle: open for extension, closed for modification.
    """

    @abstractmethod
    async def search(self, params: "SearchParams") -> list["Video"]:
        """
        Search for videos based on parameters.

        Args:
            params: Search parameters

        Returns:
            List of video results

        Raises:
            SearchProviderError: If search operation fails
            NetworkError: If network connection fails
            InvalidQueryError: If search parameters are invalid
        """
        pass

    @abstractmethod
    async def get_video_details(self, video_id: str) -> "VideoDetails":
        """
        Get detailed information about a specific video.

        Args:
            video_id: YouTube video ID

        Returns:
            Detailed video information

        Raises:
            VideoNotFoundError: If video doesn't exist or is unavailable
            NetworkError: If network connection fails
            ExtractionError: If metadata extraction fails
        """
        pass

    @abstractmethod
    async def validate_connection(self) -> bool:
        """
        Validate that the provider is working correctly.

        Returns:
            True if provider is operational, False otherwise
        """
        pass

    @abstractmethod
    async def search_playlists(self, query: str, max_results: int = 10) -> list["Playlist"]:
        """
        Search for playlists matching a query.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of playlist results

        Raises:
            SearchProviderError: If search operation fails
            NetworkError: If network connection fails
            InvalidQueryError: If search parameters are invalid
        """
        pass

    @abstractmethod
    async def get_playlist_details(self, playlist_id: str) -> "PlaylistDetails":
        """
        Get detailed information about a specific playlist.

        Args:
            playlist_id: YouTube playlist ID

        Returns:
            Detailed playlist information

        Raises:
            VideoNotFoundError: If playlist doesn't exist or is unavailable
            NetworkError: If network connection fails
            ExtractionError: If metadata extraction fails
        """
        pass

    @abstractmethod
    async def get_playlist_videos(
        self, playlist_id: str, max_results: int | None = None
    ) -> list["Video"]:
        """
        Get videos from a playlist.

        Args:
            playlist_id: YouTube playlist ID
            max_results: Maximum number of videos to return (None for all)

        Returns:
            List of videos in the playlist

        Raises:
            VideoNotFoundError: If playlist doesn't exist or is unavailable
            NetworkError: If network connection fails
            ExtractionError: If metadata extraction fails
        """
        pass


class Downloader(ABC):
    """
    Abstract base class for video/audio downloaders.
    Follows Open/Closed Principle.
    """

    @abstractmethod
    async def download_video(self, params: "DownloadParams") -> "DownloadResult":
        """
        Download a video with specified quality and format.

        Args:
            params: Download parameters

        Returns:
            Download result with file path and metadata

        Raises:
            VideoNotFoundError: If video doesn't exist
            DownloadError: If download operation fails
            DiskSpaceError: If insufficient disk space
            PermissionError: If cannot write to output directory
        """
        pass

    @abstractmethod
    async def download_audio(self, params: "DownloadParams") -> "DownloadResult":
        """
        Download audio only from a video.

        Args:
            params: Download parameters

        Returns:
            Download result with file path and metadata

        Raises:
            VideoNotFoundError: If video doesn't exist
            DownloadError: If download operation fails
            DiskSpaceError: If insufficient disk space
            PermissionError: If cannot write to output directory
        """
        pass

    @abstractmethod
    async def get_available_formats(self, video_id: str) -> dict[str, Any]:
        """
        Get list of available download formats for a video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary of available formats

        Raises:
            VideoNotFoundError: If video doesn't exist
            NetworkError: If network connection fails
        """
        pass


class ResultFormatter(ABC):
    """
    Abstract base class for result formatters.
    Follows Interface Segregation Principle: focused interface.
    """

    @abstractmethod
    def format_videos(self, videos: list["Video"]) -> str:
        """
        Format a list of videos.

        Args:
            videos: List of videos to format

        Returns:
            Formatted string representation
        """
        pass

    @abstractmethod
    def format_video_details(self, details: "VideoDetails") -> str:
        """
        Format detailed video information.

        Args:
            details: Video details to format

        Returns:
            Formatted string representation
        """
        pass

    @abstractmethod
    def format_playlists(self, playlists: list["Playlist"]) -> str:
        """
        Format a list of playlists.

        Args:
            playlists: List of playlists to format

        Returns:
            Formatted string representation
        """
        pass

    @abstractmethod
    def format_playlist_details(self, details: "PlaylistDetails") -> str:
        """
        Format detailed playlist information.

        Args:
            details: Playlist details to format

        Returns:
            Formatted string representation
        """
        pass


class ConfigProvider(Protocol):
    """
    Protocol for configuration providers.
    Follows Dependency Inversion Principle: depend on abstraction, not concretion.
    """

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        ...

    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value."""
        ...

    def get_str(self, key: str, default: str = "") -> str:
        """Get string configuration value."""
        ...
