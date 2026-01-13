"""JSON result formatter."""

import json

from ..core.interfaces import ResultFormatter
from ..models.playlist import Playlist, PlaylistDetails
from ..models.video import Video, VideoDetails


class JsonFormatter(ResultFormatter):
    """Format search results as JSON."""

    def format_videos(self, videos: list[Video]) -> str:
        """
        Format video list as JSON.

        Args:
            videos: List of videos to format

        Returns:
            JSON string representation
        """
        data = {"count": len(videos), "videos": [v.model_dump() for v in videos]}
        return json.dumps(data, indent=2, ensure_ascii=False)

    def format_video_details(self, details: VideoDetails) -> str:
        """
        Format video details as JSON.

        Args:
            details: Video details to format

        Returns:
            JSON string representation
        """
        return json.dumps(details.model_dump(), indent=2, ensure_ascii=False)

    def format_playlists(self, playlists: list[Playlist]) -> str:
        """
        Format playlist list as JSON.

        Args:
            playlists: List of playlists to format

        Returns:
            JSON string representation
        """
        data = {"count": len(playlists), "playlists": [p.model_dump() for p in playlists]}
        return json.dumps(data, indent=2, ensure_ascii=False)

    def format_playlist_details(self, details: PlaylistDetails) -> str:
        """
        Format playlist details as JSON.

        Args:
            details: Playlist details to format

        Returns:
            JSON string representation
        """
        return json.dumps(details.model_dump(), indent=2, ensure_ascii=False)
