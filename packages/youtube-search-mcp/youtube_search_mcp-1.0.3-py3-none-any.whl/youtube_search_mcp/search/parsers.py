"""Data parsers for yt-dlp search results."""

from datetime import datetime
from typing import Any

from ..models.playlist import Playlist, PlaylistDetails
from ..models.video import Video, VideoDetails
from ..utils.logger import get_logger

logger = get_logger(__name__)


class YtDlpDataParser:
    """
    Parses raw data from yt-dlp into domain models.
    Separates data transformation logic from execution logic.
    """

    def parse_video(self, data: dict[str, Any]) -> Video:
        """
        Parse yt-dlp result into Video model.

        Args:
            data: Raw video data from yt-dlp

        Returns:
            Video model instance
        """
        video_id = data.get("id", "")
        thumbnail_url = self._extract_thumbnail_url(data)

        # Extract timestamp fields and convert to upload_date
        timestamp = data.get("timestamp")
        release_timestamp = data.get("release_timestamp")
        upload_date = self._convert_timestamp_to_date(timestamp or release_timestamp)

        return Video(
            video_id=video_id,
            title=data.get("title", "Unknown"),
            url=f"https://youtube.com/watch?v={video_id}",
            duration=data.get("duration"),
            view_count=data.get("view_count"),
            uploader=data.get("uploader") or data.get("channel"),
            upload_date=upload_date,
            thumbnail=thumbnail_url,
            timestamp=timestamp,
            release_timestamp=release_timestamp,
        )

    def parse_video_details(self, data: dict[str, Any]) -> VideoDetails:
        """
        Parse detailed video information.

        Args:
            data: Raw video data from yt-dlp

        Returns:
            VideoDetails model instance
        """
        video_id = data.get("id", "")
        thumbnail_url = self._extract_thumbnail_url(data)

        # Extract timestamp fields and convert to upload_date
        timestamp = data.get("timestamp")
        release_timestamp = data.get("release_timestamp")
        upload_date = self._convert_timestamp_to_date(timestamp or release_timestamp)

        return VideoDetails(
            video_id=video_id,
            title=data.get("title", "Unknown"),
            url=f"https://youtube.com/watch?v={video_id}",
            duration=data.get("duration"),
            view_count=data.get("view_count"),
            uploader=data.get("uploader") or data.get("channel"),
            uploader_id=data.get("uploader_id") or data.get("channel_id"),
            upload_date=upload_date,
            thumbnail=thumbnail_url,
            timestamp=timestamp,
            release_timestamp=release_timestamp,
            # Extended metadata
            description=data.get("description"),
            tags=data.get("tags", []),
            categories=data.get("categories", []),
            like_count=data.get("like_count"),
            comment_count=data.get("comment_count"),
            age_limit=data.get("age_limit"),
            formats_available=len(data.get("formats", [])),
        )

    def parse_playlist(self, data: dict[str, Any]) -> Playlist:
        """
        Parse yt-dlp result into Playlist model.

        Args:
            data: Raw playlist data from yt-dlp

        Returns:
            Playlist model instance
        """
        playlist_id = data.get("id", "")

        # Get thumbnail from first video or playlist thumbnail
        thumbnail = data.get("thumbnail")
        if not thumbnail and data.get("thumbnails"):
            thumbnails = data.get("thumbnails", [])
            if thumbnails:
                thumbnail = thumbnails[-1].get("url") if isinstance(thumbnails[-1], dict) else None

        return Playlist(
            playlist_id=playlist_id,
            title=data.get("title", "Unknown"),
            url=f"https://youtube.com/playlist?list={playlist_id}",
            uploader=data.get("uploader") or data.get("channel"),
            uploader_id=data.get("uploader_id") or data.get("channel_id"),
            video_count=data.get("playlist_count") or data.get("n_entries"),
            thumbnail=thumbnail,
            description=data.get("description"),
            modified_date=data.get("modified_date"),
        )

    def parse_playlist_details(self, data: dict[str, Any]) -> PlaylistDetails:
        """
        Parse detailed playlist information.

        Args:
            data: Raw playlist data from yt-dlp

        Returns:
            PlaylistDetails model instance
        """
        playlist_id = data.get("id", "")

        # Get thumbnail from first video or playlist thumbnail
        thumbnail = data.get("thumbnail")
        if not thumbnail and data.get("thumbnails"):
            thumbnails = data.get("thumbnails", [])
            if thumbnails:
                thumbnail = thumbnails[-1].get("url") if isinstance(thumbnails[-1], dict) else None

        return PlaylistDetails(
            playlist_id=playlist_id,
            title=data.get("title", "Unknown"),
            url=f"https://youtube.com/playlist?list={playlist_id}",
            uploader=data.get("uploader") or data.get("channel"),
            uploader_id=data.get("uploader_id") or data.get("channel_id"),
            video_count=data.get("playlist_count") or len(data.get("entries", [])),
            thumbnail=thumbnail,
            description=data.get("description"),
            modified_date=data.get("modified_date"),
            availability=data.get("availability"),
            tags=data.get("tags", []),
            view_count=data.get("view_count"),
        )

    def _extract_thumbnail_url(self, data: dict[str, Any]) -> str | None:
        """
        Extract the best quality thumbnail URL from video data.

        Args:
            data: Raw video data from yt-dlp

        Returns:
            Thumbnail URL or None if not available
        """
        thumbnail_url = data.get("thumbnail")
        if isinstance(thumbnail_url, str):
            return thumbnail_url

        thumbnails = data.get("thumbnails")
        if isinstance(thumbnails, list) and len(thumbnails) > 0:
            # yt-dlp orders thumbnails by quality (ascending), so last is highest quality
            last_thumb = thumbnails[-1]
            if isinstance(last_thumb, dict):
                url = last_thumb.get("url")
                if isinstance(url, str):
                    return url

        return None

    def _convert_timestamp_to_date(self, timestamp: int | None) -> str | None:
        """
        Convert Unix timestamp to YYYYMMDD format.

        Args:
            timestamp: Unix timestamp in seconds

        Returns:
            Date string in YYYYMMDD format or None if conversion fails
        """
        if not timestamp:
            return None

        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y%m%d")
        except (ValueError, OSError, OverflowError) as e:
            logger.warning(f"Failed to convert timestamp {timestamp}: {e}")
            return None
