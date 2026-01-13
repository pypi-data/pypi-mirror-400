"""Input validation utilities."""

import re

from ..core.exceptions import InvalidQueryError


def validate_video_id(video_id: str) -> bool:
    """
    Validate YouTube video ID format.

    YouTube video IDs are typically 11 characters containing:
    - Letters (a-z, A-Z)
    - Numbers (0-9)
    - Hyphens (-)
    - Underscores (_)

    Args:
        video_id: Video ID to validate

    Returns:
        True if valid, False otherwise
    """
    if not video_id:
        return False

    # YouTube video ID pattern: 11 characters, alphanumeric plus - and _
    pattern = r"^[a-zA-Z0-9_-]{11}$"
    return bool(re.match(pattern, video_id))


def validate_query(query: str) -> str:
    """
    Validate and sanitize search query.

    Args:
        query: Search query string

    Returns:
        Sanitized query string

    Raises:
        InvalidQueryError: If query is invalid
    """
    if not query or not query.strip():
        raise InvalidQueryError("Search query cannot be empty")

    query = query.strip()

    if len(query) > 200:
        raise InvalidQueryError("Search query too long (maximum 200 characters)")

    if len(query) < 1:
        raise InvalidQueryError("Search query too short (minimum 1 character)")

    return query


def sanitize_filename(filename: str) -> str:
    """
    Remove or replace invalid characters from filename.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for Windows and Unix filesystems
    """
    # Invalid characters for Windows filenames
    invalid_chars = '<>:"/\\|?*'

    # Replace invalid characters with underscore
    for char in invalid_chars:
        filename = filename.replace(char, "_")

    # Remove leading/trailing periods and spaces
    filename = filename.strip(". ")

    # Ensure filename is not empty
    if not filename:
        filename = "unnamed"

    return filename
