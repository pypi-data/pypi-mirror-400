"""Download parameter and result models using Pydantic."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DownloadParams(BaseModel):
    """Parameters for video/audio download."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "quality": "high",
                "output_dir": "C:\\Users\\Downloads",
                "format": "mp4",
                "download_type": "video",
            }
        }
    )

    video_id: str = Field(..., min_length=11, max_length=11, description="YouTube video ID")
    quality: Literal["best", "high", "medium", "low"] = Field(
        "best", description="Quality preset for download"
    )
    output_dir: str | None = Field(
        None, description="Output directory path (uses config default if not specified)"
    )
    format: str = Field("mp4", description="Output format (e.g., mp4, webm, mp3, m4a)")
    download_type: Literal["video", "audio"] = Field(
        "video", description="Type of download: video or audio only"
    )


class DownloadResult(BaseModel):
    """Result of a download operation."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "video_id": "dQw4w9WgXcQ",
                "title": "Rick Astley - Never Gonna Give You Up",
                "file_path": "C:\\Users\\Downloads\\Rick Astley - Never Gonna Give You Up.mp4",
                "file_size": 52428800,
                "duration": 212,
                "format": "mp4",
                "quality": "high",
                "error": None,
            }
        }
    )

    success: bool = Field(..., description="Whether download was successful")
    video_id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Video title")
    file_path: str | None = Field(None, description="Path to downloaded file")
    file_size: int | None = Field(None, description="File size in bytes")
    duration: int | None = Field(None, description="Video duration in seconds")
    format: str = Field(..., description="Downloaded format")
    quality: str = Field(..., description="Downloaded quality")
    error: str | None = Field(None, description="Error message if download failed")
