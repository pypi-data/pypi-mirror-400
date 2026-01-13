"""YouTube video/audio downloader implementation using yt-dlp."""

import asyncio
import os
from typing import Any

import yt_dlp

from ..core.exceptions import (
    DiskSpaceError,
    DownloadError,
    FFmpegNotFoundError,
    NetworkError,
    VideoNotFoundError,
)
from ..core.exceptions import (
    PermissionError as MCPPermissionError,
)
from ..core.interfaces import Downloader
from ..models.download_params import DownloadParams, DownloadResult
from ..search.retry_decorator import async_retry
from ..utils.file_utils import (
    check_ffmpeg_available,
    get_ffmpeg_path,
    get_file_size,
    validate_download_path,
)
from ..utils.logger import get_logger
from .progress_tracker import create_progress_hook
from .quality_presets import (
    get_audio_format_string,
    get_audio_postprocessors,
    get_video_format_string,
)

logger = get_logger(__name__)


class YtDlpDownloader(Downloader):
    """
    yt-dlp implementation of Downloader interface.
    Handles video and audio downloads with quality presets.
    """

    def __init__(
        self,
        default_output_dir: str = "downloads",
        min_disk_space_mb: int = 100,
    ) -> None:
        """
        Initialize yt-dlp downloader.

        Args:
            default_output_dir: Default download directory
            min_disk_space_mb: Minimum required disk space in MB
        """
        self._default_output_dir = default_output_dir
        self._min_disk_space_mb = min_disk_space_mb

    @async_retry(max_attempts=3, exceptions=(NetworkError,))
    async def download_video(self, params: DownloadParams) -> DownloadResult:
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
        logger.info(
            f"Starting video download: {params.video_id} "
            f"(quality={params.quality}, format={params.format})"
        )
        return await self._download(params, is_video=True)

    @async_retry(max_attempts=3, exceptions=(NetworkError,))
    async def download_audio(self, params: DownloadParams) -> DownloadResult:
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
        logger.info(
            f"Starting audio download: {params.video_id} "
            f"(quality={params.quality}, format={params.format})"
        )
        return await self._download(params, is_video=False)

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
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            ydl_opts = {
                "quiet": True,
                "skip_download": True,
                "ffmpeg_location": get_ffmpeg_path(),
            }

            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, self._extract_info, url, ydl_opts)

            formats = info.get("formats", [])
            return {
                "video_id": video_id,
                "title": info.get("title", "Unknown"),
                "format_count": len(formats),
                "formats": [
                    {
                        "format_id": f.get("format_id"),
                        "ext": f.get("ext"),
                        "resolution": f.get("resolution"),
                        "filesize": f.get("filesize"),
                    }
                    for f in formats
                ],
            }

        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e).lower()
            if "video unavailable" in error_msg:
                raise VideoNotFoundError(f"Video {video_id} not found", original_error=e)
            raise NetworkError(f"Network error getting formats: {str(e)}", original_error=e)

    async def _download(self, params: DownloadParams, is_video: bool) -> DownloadResult:
        """
        Common download logic for both video and audio.

        Args:
            params: Download parameters
            is_video: True for video download, False for audio

        Returns:
            Download result with file path and metadata

        Raises:
            FFmpegNotFoundError: If FFmpeg is not installed
            VideoNotFoundError: If video doesn't exist
            DownloadError: If download operation fails
            DiskSpaceError: If insufficient disk space
            PermissionError: If cannot write to output directory
        """
        # Check FFmpeg availability before starting download
        check_ffmpeg_available()

        output_dir = self._validate_output_directory(params.output_dir)

        try:
            ydl_opts = (
                self._build_video_options(params, output_dir)
                if is_video
                else self._build_audio_options(params, output_dir)
            )

            loop = asyncio.get_event_loop()
            result_info = await loop.run_in_executor(
                None, self._execute_download, params.video_id, ydl_opts
            )

            file_path = self._extract_file_path(result_info)
            file_size = get_file_size(file_path)

            logger.info(f"{'Video' if is_video else 'Audio'} download completed: {file_path}")

            return DownloadResult(
                success=True,
                video_id=params.video_id,
                title=result_info.get("title", "Unknown"),
                file_path=file_path,
                file_size=file_size,
                duration=result_info.get("duration"),
                format=params.format,
                quality=params.quality,
            )

        except yt_dlp.utils.DownloadError as e:
            self._handle_ytdlp_error(e, params.video_id)
        except (DiskSpaceError, MCPPermissionError):
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during download: {e}")
            raise DownloadError(f"Unexpected error during download: {str(e)}", original_error=e)

    def _validate_output_directory(self, output_dir: str | None) -> str:
        """
        Validate and prepare output directory.

        Args:
            output_dir: Optional output directory path

        Returns:
            Validated output directory path

        Raises:
            DiskSpaceError: If insufficient disk space
            PermissionError: If cannot write to directory
        """
        output_dir = output_dir or self._default_output_dir
        is_valid, error_msg = validate_download_path(output_dir, self._min_disk_space_mb)

        if not is_valid:
            if "disk space" in error_msg.lower():
                raise DiskSpaceError(error_msg)
            else:
                raise MCPPermissionError(error_msg)

        return output_dir

    def _extract_file_path(self, result_info: dict[str, Any]) -> str:
        """
        Extract downloaded file path from yt-dlp result.

        Args:
            result_info: yt-dlp result dictionary

        Returns:
            Downloaded file path

        Raises:
            DownloadError: If file path cannot be determined or file doesn't exist
        """
        downloaded_file = (
            result_info.get("filepath")
            or result_info.get("_filename")
            or result_info.get("filename")
            or result_info.get("requested_downloads", [{}])[0].get("filepath")
        )

        if not downloaded_file or not os.path.exists(downloaded_file):
            logger.error(f"Available keys in result_info: {list(result_info.keys())}")
            raise DownloadError(f"Download completed but file not found: {downloaded_file}")

        return downloaded_file

    def _handle_ytdlp_error(self, e: yt_dlp.utils.DownloadError, video_id: str) -> None:
        """
        Handle yt-dlp download errors and convert to appropriate exceptions.

        Args:
            e: yt-dlp DownloadError
            video_id: Video ID being downloaded

        Raises:
            VideoNotFoundError: If video unavailable
            NetworkError: If network error
            DownloadError: For other download failures
        """
        error_msg = str(e).lower()

        if "video unavailable" in error_msg or "private video" in error_msg:
            raise VideoNotFoundError(f"Video {video_id} not found or unavailable", original_error=e)

        if "unable to download" in error_msg or "connection" in error_msg:
            raise NetworkError(f"Network error during download: {str(e)}", original_error=e)

        raise DownloadError(f"Download failed: {str(e)}", original_error=e)

    def _build_video_options(self, params: DownloadParams, output_dir: str) -> dict[str, Any]:
        """
        Build yt-dlp options for video download.

        Args:
            params: Download parameters
            output_dir: Output directory path

        Returns:
            Dictionary of yt-dlp options
        """
        format_string = get_video_format_string(params.quality)
        output_template = os.path.join(output_dir, "%(title)s.%(ext)s")

        return {
            "format": format_string,
            "outtmpl": output_template,
            "merge_output_format": params.format,
            "progress_hooks": [create_progress_hook(params.video_id)],
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "ffmpeg_location": get_ffmpeg_path(),
            "concurrent_fragment_downloads": 8,
            "postprocessors": [
                {
                    "key": "FFmpegVideoRemuxer",
                    "preferedformat": "mp4",
                }
            ],
        }

    def _build_audio_options(self, params: DownloadParams, output_dir: str) -> dict[str, Any]:
        """
        Build yt-dlp options for audio download.

        Args:
            params: Download parameters
            output_dir: Output directory path

        Returns:
            Dictionary of yt-dlp options
        """
        format_string = get_audio_format_string(params.quality)
        postprocessors = get_audio_postprocessors(params.format)
        output_template = os.path.join(output_dir, "%(title)s.%(ext)s")

        return {
            "format": format_string,
            "outtmpl": output_template,
            "postprocessors": postprocessors,
            "progress_hooks": [create_progress_hook(params.video_id)],
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "ffmpeg_location": get_ffmpeg_path(),
            "concurrent_fragment_downloads": 8,
        }

    def _execute_download(self, video_id: str, ydl_opts: dict[str, Any]) -> dict[str, Any]:
        """
        Execute download synchronously (runs in thread pool).

        Args:
            video_id: YouTube video ID
            ydl_opts: yt-dlp options

        Returns:
            Video information dictionary with filepath added
        """
        url = f"https://www.youtube.com/watch?v={video_id}"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if info:
                if info.get("requested_downloads"):
                    info["filepath"] = info["requested_downloads"][0].get("filepath")
                else:
                    base_filename = ydl.prepare_filename(info)

                    if ydl_opts.get("merge_output_format"):
                        base_name = os.path.splitext(base_filename)[0]
                        info["filepath"] = f"{base_name}.{ydl_opts['merge_output_format']}"
                    else:
                        info["filepath"] = base_filename

            return info

    def _extract_info(self, url: str, ydl_opts: dict[str, Any]) -> dict[str, Any]:
        """
        Extract video info without downloading.

        Args:
            url: Video URL
            ydl_opts: yt-dlp options

        Returns:
            Video information dictionary
        """
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
