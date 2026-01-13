"""Video data models using Pydantic."""


from pydantic import BaseModel, ConfigDict, Field


class Video(BaseModel):
    """Basic video information from search results."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "title": "Rick Astley - Never Gonna Give You Up",
                "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "duration": 212,
                "view_count": 1400000000,
                "uploader": "Rick Astley",
                "upload_date": "20091025",
                "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            }
        }
    )

    video_id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Video title")
    url: str = Field(..., description="Video URL")
    duration: int | None = Field(None, description="Duration in seconds")
    view_count: int | None = Field(None, description="Number of views")
    uploader: str | None = Field(None, description="Channel name")
    upload_date: str | None = Field(None, description="Upload date (YYYYMMDD format)")
    thumbnail: str | None = Field(None, description="Thumbnail URL (highest quality)")

    # Original yt-dlp data fields
    # thumbnails: Optional[list[dict]] = Field(None, description="All available thumbnails with different resolutions")
    timestamp: int | None = Field(None, description="Upload timestamp (Unix timestamp)")
    release_timestamp: int | None = Field(None, description="Release timestamp (Unix timestamp)")


class VideoDetails(Video):
    """Detailed video information with extended metadata."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "title": "Rick Astley - Never Gonna Give You Up",
                "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "duration": 212,
                "view_count": 1400000000,
                "uploader": "Rick Astley",
                "uploader_id": "UCuAXFkgsw1L7xaCfnd5JJOw",
                "upload_date": "20091025",
                "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
                "description": "The official video for Never Gonna Give You Up...",
                "tags": ["rick astley", "never gonna give you up", "80s music"],
                "categories": ["Music"],
                "like_count": 15000000,
                "comment_count": 2500000,
                "age_limit": 0,
                "formats_available": 25,
            }
        }
    )

    description: str | None = Field(None, description="Video description")
    tags: list[str] = Field(default_factory=list, description="Video tags")
    categories: list[str] = Field(default_factory=list, description="Video categories")
    like_count: int | None = Field(None, description="Number of likes")
    comment_count: int | None = Field(None, description="Number of comments")
    uploader_id: str | None = Field(None, description="Channel ID")
    age_limit: int | None = Field(None, description="Age restriction (0 = no restriction)")
    formats_available: int = Field(0, description="Number of available download formats")
