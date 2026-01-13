"""Playlist data models using Pydantic."""


from pydantic import BaseModel, ConfigDict, Field


class Playlist(BaseModel):
    """Basic playlist information from search results."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "playlist_id": "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
                "title": "Python Tutorial for Beginners",
                "url": "https://youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
                "uploader": "Programming with Mosh",
                "uploader_id": "UCWv7vMbMWH4-V0ZXdmDpPBA",
                "video_count": 45,
                "thumbnail": "https://i.ytimg.com/vi/abc123/maxresdefault.jpg",
                "description": "Complete Python tutorial series...",
            }
        }
    )

    playlist_id: str = Field(..., description="YouTube playlist ID")
    title: str = Field(..., description="Playlist title")
    url: str = Field(..., description="Playlist URL")
    uploader: str | None = Field(None, description="Channel name")
    uploader_id: str | None = Field(None, description="Channel ID")
    video_count: int | None = Field(None, description="Number of videos in playlist")
    thumbnail: str | None = Field(None, description="Playlist thumbnail URL")
    description: str | None = Field(None, description="Playlist description")
    modified_date: str | None = Field(None, description="Last modified date (YYYYMMDD format)")


class PlaylistDetails(Playlist):
    """Detailed playlist information with extended metadata."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "playlist_id": "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
                "title": "Python Tutorial for Beginners",
                "url": "https://youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
                "uploader": "Programming with Mosh",
                "uploader_id": "UCWv7vMbMWH4-V0ZXdmDpPBA",
                "video_count": 45,
                "thumbnail": "https://i.ytimg.com/vi/abc123/maxresdefault.jpg",
                "description": "Complete Python tutorial series...",
                "modified_date": "20231215",
                "availability": "public",
                "tags": ["python", "programming", "tutorial"],
                "view_count": 1500000,
            }
        }
    )

    availability: str | None = Field(
        None, description="Playlist availability (public, unlisted, private)"
    )
    tags: list[str] = Field(default_factory=list, description="Playlist tags")
    view_count: int | None = Field(None, description="Total views across all videos")
