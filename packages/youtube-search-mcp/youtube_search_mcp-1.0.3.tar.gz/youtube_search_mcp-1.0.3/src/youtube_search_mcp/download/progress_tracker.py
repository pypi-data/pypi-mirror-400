"""Download progress tracking utilities."""

from collections.abc import Callable
from typing import Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


class ProgressTracker:
    """Track download progress from yt-dlp hooks."""

    def __init__(self, video_id: str, callback: Callable[[dict], None] | None = None) -> None:
        """
        Initialize progress tracker.

        Args:
            video_id: YouTube video ID being downloaded
            callback: Optional callback function to receive progress updates
        """
        self.video_id = video_id
        self.callback = callback
        self.total_bytes: int | None = None
        self.downloaded_bytes: int = 0
        self.speed: float | None = None
        self.eta: int | None = None

    def hook(self, d: dict[str, Any]) -> None:
        """
        Progress hook for yt-dlp.

        Args:
            d: Progress dictionary from yt-dlp
        """
        status = d.get("status")

        if status == "downloading":
            self._handle_downloading(d)
        elif status == "finished":
            self._handle_finished(d)
        elif status == "error":
            self._handle_error(d)

    def _handle_downloading(self, d: dict[str, Any]) -> None:
        """Handle downloading status update."""
        self.total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate")
        self.downloaded_bytes = d.get("downloaded_bytes", 0)
        self.speed = d.get("speed")
        self.eta = d.get("eta")

        percent_str = d.get("_percent_str", "N/A")
        speed_str = d.get("_speed_str", "N/A")
        eta_str = d.get("_eta_str", "N/A")

        logger.info(f"Downloading {self.video_id}: {percent_str} at {speed_str} ETA: {eta_str}")

        if self.callback:
            self.callback(
                {
                    "status": "downloading",
                    "video_id": self.video_id,
                    "total_bytes": self.total_bytes,
                    "downloaded_bytes": self.downloaded_bytes,
                    "percent": percent_str,
                    "speed": speed_str,
                    "eta": eta_str,
                }
            )

    def _handle_finished(self, d: dict[str, Any]) -> None:
        """Handle finished status update."""
        filename = d.get("filename", "unknown")
        logger.info(f"Download finished: {filename}")

        if self.callback:
            self.callback(
                {
                    "status": "finished",
                    "video_id": self.video_id,
                    "filename": filename,
                }
            )

    def _handle_error(self, d: dict[str, Any]) -> None:
        """Handle error status update."""
        error_msg = d.get("error", "Unknown error")
        logger.error(f"Download error for {self.video_id}: {error_msg}")

        if self.callback:
            self.callback(
                {
                    "status": "error",
                    "video_id": self.video_id,
                    "error": error_msg,
                }
            )


def create_progress_hook(video_id: str) -> Callable[[dict], None]:
    """
    Create a progress hook function for yt-dlp.

    Args:
        video_id: YouTube video ID

    Returns:
        Progress hook function
    """
    tracker = ProgressTracker(video_id)
    return tracker.hook
