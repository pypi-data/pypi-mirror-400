"""Download-related MCP tools."""

import json

from fastmcp import FastMCP

from ..core.exceptions import (
    DiskSpaceError,
    DownloadError,
    FFmpegNotFoundError,
    InvalidQueryError,
    NetworkError,
    VideoNotFoundError,
)
from ..core.exceptions import (
    PermissionError as MCPPermissionError,
)
from ..models.download_params import DownloadParams
from ..utils.logger import get_logger
from ..utils.validators import validate_video_id
from .dependencies import get_downloader

logger = get_logger(__name__)


def register_download_tools(mcp: FastMCP) -> None:
    """
    Register all download-related tools with the MCP server.

    Args:
        mcp: FastMCP server instance
    """

    @mcp.tool()
    async def download_video(
        video_id: str,
        quality: str = "best",
        output_dir: str | None = None,
        format: str = "mp4",
    ) -> str:
        """
        Download a YouTube video with configurable quality.

        Args:
            video_id: YouTube video ID (11 characters)
            quality: Quality preset - "best", "high" (1080p), "medium" (720p), "low" (480p)
            output_dir: Download directory path (uses config default if not specified)
            format: Output format - "mp4", "webm", "mkv" (default: "mp4")

        Returns:
            JSON with download status, file path, file size, and metadata

        Example:
            download_video("dQw4w9WgXcQ", quality="high", format="mp4")
        """
        try:
            logger.info(
                f"Download video request: video_id='{video_id}', quality='{quality}', format='{format}'"
            )

            # Validate video ID
            if not validate_video_id(video_id):
                raise InvalidQueryError(f"Invalid video ID format: {video_id}")

            # Create download parameters
            params = DownloadParams(
                video_id=video_id,
                quality=quality,
                output_dir=output_dir,
                format=format,
                download_type="video",
            )

            # Execute download
            downloader = get_downloader()
            result = await downloader.download_video(params)

            logger.info(f"Video download completed: {result.file_path}")
            return json.dumps(result.model_dump(), indent=2)

        except FFmpegNotFoundError as e:
            logger.error(f"FFmpeg not found: {e.message}")
            return json.dumps(
                {
                    "success": False,
                    "error": "ffmpeg_not_found",
                    "message": e.message,
                }
            )
        except InvalidQueryError as e:
            logger.warning(f"Invalid parameters: {e.message}")
            return json.dumps(
                {"success": False, "error": "invalid_parameters", "message": e.message}
            )
        except VideoNotFoundError as e:
            logger.warning(f"Video not found: {e.message}")
            return json.dumps(
                {
                    "success": False,
                    "error": "video_not_found",
                    "message": "Video not found or unavailable.",
                }
            )
        except DiskSpaceError as e:
            logger.error(f"Disk space error: {e.message}")
            return json.dumps({"success": False, "error": "disk_space", "message": e.message})
        except MCPPermissionError as e:
            logger.error(f"Permission error: {e.message}")
            return json.dumps(
                {"success": False, "error": "permission_denied", "message": e.message}
            )
        except NetworkError as e:
            logger.error(f"Network error: {e.message}")
            return json.dumps(
                {
                    "success": False,
                    "error": "network_error",
                    "message": "Download failed due to network error.",
                }
            )
        except DownloadError as e:
            logger.error(f"Download error: {e.message}")
            return json.dumps({"success": False, "error": "download_failed", "message": e.message})
        except Exception:
            logger.exception("Unexpected error in download_video")
            return json.dumps(
                {
                    "success": False,
                    "error": "internal_error",
                    "message": "An unexpected error occurred.",
                }
            )

    @mcp.tool()
    async def download_audio(
        video_id: str,
        quality: str = "best",
        output_dir: str | None = None,
        format: str = "mp3",
    ) -> str:
        """
        Download audio only from a YouTube video.

        Args:
            video_id: YouTube video ID (11 characters)
            quality: Audio quality preset - "best", "high" (320kbps), "medium" (192kbps), "low" (128kbps)
            output_dir: Download directory path (uses config default if not specified)
            format: Output format - "mp3", "m4a", "opus", "wav" (default: "mp3")

        Returns:
            JSON with download status, file path, file size, and metadata

        Example:
            download_audio("dQw4w9WgXcQ", quality="high", format="mp3")
        """
        try:
            logger.info(
                f"Download audio request: video_id='{video_id}', quality='{quality}', format='{format}'"
            )

            # Validate video ID
            if not validate_video_id(video_id):
                raise InvalidQueryError(f"Invalid video ID format: {video_id}")

            # Create download parameters
            params = DownloadParams(
                video_id=video_id,
                quality=quality,
                output_dir=output_dir,
                format=format,
                download_type="audio",
            )

            # Execute download
            downloader = get_downloader()
            result = await downloader.download_audio(params)

            logger.info(f"Audio download completed: {result.file_path}")
            return json.dumps(result.model_dump(), indent=2)

        except FFmpegNotFoundError as e:
            logger.error(f"FFmpeg not found: {e.message}")
            return json.dumps(
                {
                    "success": False,
                    "error": "ffmpeg_not_found",
                    "message": e.message,
                }
            )
        except InvalidQueryError as e:
            logger.warning(f"Invalid parameters: {e.message}")
            return json.dumps(
                {"success": False, "error": "invalid_parameters", "message": e.message}
            )
        except VideoNotFoundError as e:
            logger.warning(f"Video not found: {e.message}")
            return json.dumps(
                {
                    "success": False,
                    "error": "video_not_found",
                    "message": "Video not found or unavailable.",
                }
            )
        except DiskSpaceError as e:
            logger.error(f"Disk space error: {e.message}")
            return json.dumps({"success": False, "error": "disk_space", "message": e.message})
        except MCPPermissionError as e:
            logger.error(f"Permission error: {e.message}")
            return json.dumps(
                {"success": False, "error": "permission_denied", "message": e.message}
            )
        except NetworkError as e:
            logger.error(f"Network error: {e.message}")
            return json.dumps(
                {
                    "success": False,
                    "error": "network_error",
                    "message": "Download failed due to network error.",
                }
            )
        except DownloadError as e:
            logger.error(f"Download error: {e.message}")
            return json.dumps({"success": False, "error": "download_failed", "message": e.message})
        except Exception:
            logger.exception("Unexpected error in download_audio")
            return json.dumps(
                {
                    "success": False,
                    "error": "internal_error",
                    "message": "An unexpected error occurred.",
                }
            )
