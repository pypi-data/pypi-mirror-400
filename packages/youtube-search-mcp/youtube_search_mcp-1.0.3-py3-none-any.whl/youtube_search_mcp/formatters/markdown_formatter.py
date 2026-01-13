"""Markdown result formatter."""

from ..core.interfaces import ResultFormatter
from ..models.playlist import Playlist, PlaylistDetails
from ..models.video import Video, VideoDetails


class MarkdownFormatter(ResultFormatter):
    """Format search results as Markdown."""

    def format_videos(self, videos: list[Video]) -> str:
        """
        Format video list as Markdown.

        Args:
            videos: List of videos to format

        Returns:
            Markdown string representation
        """
        lines = [f"# Search Results ({len(videos)} videos)\n"]

        for i, video in enumerate(videos, 1):
            lines.append(f"## {i}. {video.title}")
            lines.append(f"- **Video ID**: `{video.video_id}`")
            lines.append(f"- **URL**: {video.url}")

            if video.uploader:
                lines.append(f"- **Uploader**: {video.uploader}")

            if video.duration:
                minutes, seconds = divmod(video.duration, 60)
                hours, minutes = divmod(minutes, 60)
                if hours > 0:
                    duration_str = f"{hours}h {minutes}m {seconds}s"
                else:
                    duration_str = f"{minutes}m {seconds}s"
                lines.append(f"- **Duration**: {duration_str}")

            if video.view_count is not None:
                lines.append(f"- **Views**: {video.view_count:,}")

            if video.upload_date:
                # Format YYYYMMDD to YYYY-MM-DD
                date = video.upload_date
                if len(date) == 8:
                    formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
                    lines.append(f"- **Upload Date**: {formatted_date}")

            if video.thumbnail:
                lines.append(f"- **Thumbnail**: {video.thumbnail}")

            lines.append("")  # Empty line between videos

        return "\n".join(lines)

    def format_video_details(self, details: VideoDetails) -> str:
        """
        Format video details as Markdown.

        Args:
            details: Video details to format

        Returns:
            Markdown string representation
        """
        lines = [f"# {details.title}\n"]

        # Basic Information
        lines.append("## Basic Information")
        lines.append(f"- **Video ID**: `{details.video_id}`")
        lines.append(f"- **URL**: {details.url}")

        if details.uploader:
            lines.append(f"- **Uploader**: {details.uploader}")

        if details.uploader_id:
            lines.append(f"- **Channel ID**: `{details.uploader_id}`")

        if details.duration:
            minutes, seconds = divmod(details.duration, 60)
            hours, minutes = divmod(minutes, 60)
            if hours > 0:
                duration_str = f"{hours}h {minutes}m {seconds}s"
            else:
                duration_str = f"{minutes}m {seconds}s"
            lines.append(f"- **Duration**: {duration_str}")

        if details.upload_date:
            # Format YYYYMMDD to YYYY-MM-DD
            date = details.upload_date
            if len(date) == 8:
                formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
                lines.append(f"- **Upload Date**: {formatted_date}")

        # Statistics
        lines.append("\n## Statistics")

        if details.view_count is not None:
            lines.append(f"- **Views**: {details.view_count:,}")

        if details.like_count is not None:
            lines.append(f"- **Likes**: {details.like_count:,}")

        if details.comment_count is not None:
            lines.append(f"- **Comments**: {details.comment_count:,}")

        # Description
        if details.description:
            lines.append("\n## Description")
            # Truncate very long descriptions
            description = details.description
            if len(description) > 500:
                description = description[:500] + "..."
            lines.append(description)

        # Tags
        if details.tags:
            lines.append("\n## Tags")
            # Show first 20 tags
            tags = details.tags[:20]
            lines.append(", ".join(f"`{tag}`" for tag in tags))
            if len(details.tags) > 20:
                lines.append(f"\n*...and {len(details.tags) - 20} more tags*")

        # Categories
        if details.categories:
            lines.append("\n## Categories")
            lines.append(", ".join(details.categories))

        # Technical Info
        lines.append("\n## Technical Information")

        if details.age_limit is not None:
            age_str = "No age restriction" if details.age_limit == 0 else f"{details.age_limit}+"
            lines.append(f"- **Age Restriction**: {age_str}")

        if details.formats_available:
            lines.append(f"- **Available Formats**: {details.formats_available}")

        return "\n".join(lines)

    def format_playlists(self, playlists: list[Playlist]) -> str:
        """
        Format playlist list as Markdown.

        Args:
            playlists: List of playlists to format

        Returns:
            Markdown string representation
        """
        lines = [f"# Playlist Search Results ({len(playlists)} playlists)\n"]

        for i, playlist in enumerate(playlists, 1):
            lines.append(f"## {i}. {playlist.title}")
            lines.append(f"- **Playlist ID**: `{playlist.playlist_id}`")
            lines.append(f"- **URL**: {playlist.url}")

            if playlist.uploader:
                lines.append(f"- **Creator**: {playlist.uploader}")

            if playlist.video_count is not None:
                lines.append(f"- **Videos**: {playlist.video_count:,}")

            if playlist.description:
                # Truncate long descriptions
                description = playlist.description
                if len(description) > 150:
                    description = description[:150] + "..."
                lines.append(f"- **Description**: {description}")

            if playlist.thumbnail:
                lines.append(f"- **Thumbnail**: {playlist.thumbnail}")

            lines.append("")  # Empty line between playlists

        return "\n".join(lines)

    def format_playlist_details(self, details: PlaylistDetails) -> str:
        """
        Format playlist details as Markdown.

        Args:
            details: Playlist details to format

        Returns:
            Markdown string representation
        """
        lines = [f"# {details.title}\n"]

        # Basic Information
        lines.append("## Basic Information")
        lines.append(f"- **Playlist ID**: `{details.playlist_id}`")
        lines.append(f"- **URL**: {details.url}")

        if details.uploader:
            lines.append(f"- **Creator**: {details.uploader}")

        if details.uploader_id:
            lines.append(f"- **Channel ID**: `{details.uploader_id}`")

        if details.video_count is not None:
            lines.append(f"- **Total Videos**: {details.video_count:,}")

        if details.availability:
            lines.append(f"- **Availability**: {details.availability}")

        if details.modified_date:
            # Format YYYYMMDD to YYYY-MM-DD
            date = details.modified_date
            if len(date) == 8:
                formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
                lines.append(f"- **Last Modified**: {formatted_date}")

        # Statistics
        if details.view_count is not None:
            lines.append("\n## Statistics")
            lines.append(f"- **Total Views**: {details.view_count:,}")

        # Description
        if details.description:
            lines.append("\n## Description")
            # Truncate very long descriptions
            description = details.description
            if len(description) > 500:
                description = description[:500] + "..."
            lines.append(description)

        # Tags
        if details.tags:
            lines.append("\n## Tags")
            # Show first 20 tags
            tags = details.tags[:20]
            lines.append(", ".join(f"`{tag}`" for tag in tags))
            if len(details.tags) > 20:
                lines.append(f"\n*...and {len(details.tags) - 20} more tags*")

        return "\n".join(lines)
