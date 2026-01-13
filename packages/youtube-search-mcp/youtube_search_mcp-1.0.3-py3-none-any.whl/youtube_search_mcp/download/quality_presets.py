"""Quality preset definitions for video and audio downloads."""

from typing import Literal

# Video Quality Presets
# These map quality levels to yt-dlp format selection strings
# Note: Using pre-merged formats first to avoid ffmpeg dependency
VIDEO_PRESETS: dict[str, str] = {
    "best": "best[ext=mp4][vcodec^=avc]/bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best",
    "high": "best[height<=1080][ext=mp4][vcodec^=avc]/bestvideo[height<=1080][ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]",
    "medium": "best[height<=720][ext=mp4][vcodec^=avc]/bestvideo[height<=720][ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]",
    "low": "best[height<=480][ext=mp4][vcodec^=avc]/bestvideo[height<=480][ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]",
}

# Audio Quality Presets
# These map quality levels to yt-dlp format selection strings
AUDIO_PRESETS: dict[str, str] = {
    "best": "bestaudio/best",
    "high": "bestaudio[abr<=320]/bestaudio",
    "medium": "bestaudio[abr<=192]/bestaudio",
    "low": "bestaudio[abr<=128]/bestaudio",
}

# Post-processing options for audio extraction
AUDIO_POST_PROCESSORS: dict[str, list[dict]] = {
    "mp3": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "320",
        }
    ],
    "m4a": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
            "preferredquality": "256",
        }
    ],
    "opus": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "opus",
            "preferredquality": "192",
        }
    ],
    "wav": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
        }
    ],
}


def get_video_format_string(quality: Literal["best", "high", "medium", "low"]) -> str:
    """
    Get yt-dlp format string for video quality preset.

    Args:
        quality: Quality preset name

    Returns:
        yt-dlp format selection string
    """
    return VIDEO_PRESETS.get(quality, VIDEO_PRESETS["best"])


def get_audio_format_string(quality: Literal["best", "high", "medium", "low"]) -> str:
    """
    Get yt-dlp format string for audio quality preset.

    Args:
        quality: Quality preset name

    Returns:
        yt-dlp format selection string
    """
    return AUDIO_PRESETS.get(quality, AUDIO_PRESETS["best"])


def get_audio_postprocessors(format: str) -> list[dict]:
    """
    Get post-processor configuration for audio format.

    Args:
        format: Audio format (mp3, m4a, opus, wav)

    Returns:
        List of post-processor dictionaries
    """
    return AUDIO_POST_PROCESSORS.get(format.lower(), AUDIO_POST_PROCESSORS["mp3"])
