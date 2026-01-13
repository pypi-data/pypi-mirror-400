"""Custom exception hierarchy for YouTube Search MCP."""



class YouTubeSearchError(Exception):
    """Base exception for all YouTube search and download errors."""

    def __init__(self, message: str, original_error: Exception | None = None) -> None:
        """
        Initialize YouTube search error.

        Args:
            message: Error message
            original_error: Original exception that caused this error
        """
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class SearchProviderError(YouTubeSearchError):
    """Raised when search provider encounters an error."""

    pass


class VideoNotFoundError(YouTubeSearchError):
    """Raised when a video cannot be found or is unavailable."""

    pass


class InvalidQueryError(YouTubeSearchError):
    """Raised when search query or parameters are invalid."""

    pass


class NetworkError(YouTubeSearchError):
    """Raised when network operations fail."""

    pass


class ExtractionError(YouTubeSearchError):
    """Raised when video metadata extraction fails."""

    pass


class RateLimitError(YouTubeSearchError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        retry_after: int | None = None,
        original_error: Exception | None = None,
    ) -> None:
        """
        Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            original_error: Original exception
        """
        super().__init__(message, original_error)
        self.retry_after = retry_after


class DownloadError(YouTubeSearchError):
    """Raised when download operation fails."""

    pass


class DiskSpaceError(YouTubeSearchError):
    """Raised when insufficient disk space is available."""

    pass


class PermissionError(YouTubeSearchError):
    """Raised when file system permission errors occur."""

    pass


class FFmpegNotFoundError(YouTubeSearchError):
    """Raised when FFmpeg is not installed or not found in PATH."""

    pass
