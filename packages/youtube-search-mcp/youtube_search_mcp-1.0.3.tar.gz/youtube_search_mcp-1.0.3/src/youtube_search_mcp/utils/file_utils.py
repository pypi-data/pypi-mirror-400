"""File system utilities for download operations."""

import os
import platform
import shutil
import sys
from pathlib import Path

from ..core.exceptions import FFmpegNotFoundError
from ..core.exceptions import PermissionError as MCPPermissionError


def check_disk_space(path: str, required_mb: int) -> bool:
    """
    Check if sufficient disk space is available.

    Args:
        path: Directory path to check
        required_mb: Required space in megabytes

    Returns:
        True if sufficient space available, False otherwise
    """
    try:
        stat = shutil.disk_usage(path)
        available_mb = stat.free / (1024 * 1024)
        return available_mb >= required_mb
    except Exception:
        # If we can't check, assume there's enough space
        return True


def ensure_directory_exists(directory: str) -> None:
    """
    Ensure directory exists, create if necessary.

    Args:
        directory: Directory path

    Raises:
        PermissionError: If cannot create directory
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise MCPPermissionError(f"Cannot create directory {directory}: {str(e)}", original_error=e)


def check_directory_writable(directory: str) -> bool:
    """
    Check if directory is writable.

    Args:
        directory: Directory path to check

    Returns:
        True if writable, False otherwise
    """
    try:
        # Try to create a test file
        test_file = Path(directory) / ".write_test"
        test_file.touch()
        test_file.unlink()
        return True
    except Exception:
        return False


def get_file_size(file_path: str) -> int | None:
    """
    Get file size in bytes.

    Args:
        file_path: Path to file

    Returns:
        File size in bytes, or None if file doesn't exist
    """
    try:
        return Path(file_path).stat().st_size
    except Exception:
        return None


def validate_download_path(output_dir: str, required_mb: int = 100) -> tuple[bool, str | None]:
    """
    Validate download path for sufficient space and write permissions.

    Args:
        output_dir: Output directory path
        required_mb: Required disk space in megabytes

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Ensure directory exists
    try:
        ensure_directory_exists(output_dir)
    except MCPPermissionError as e:
        return False, str(e)

    # Check write permissions
    if not check_directory_writable(output_dir):
        return False, f"Directory is not writable: {output_dir}"

    # Check disk space
    if not check_disk_space(output_dir, required_mb):
        available = shutil.disk_usage(output_dir).free / (1024 * 1024)
        return (
            False,
            f"Insufficient disk space. Required: {required_mb}MB, Available: {available:.1f}MB",
        )

    return True, None


def get_unique_filename(directory: str, filename: str) -> str:
    """
    Get unique filename by appending number if file already exists.

    Args:
        directory: Directory path
        filename: Desired filename

    Returns:
        Unique filename
    """
    base_path = Path(directory) / filename
    if not base_path.exists():
        return filename

    # Split name and extension
    stem = base_path.stem
    suffix = base_path.suffix

    # Try appending numbers until we find a unique name
    counter = 1
    while True:
        new_name = f"{stem} ({counter}){suffix}"
        new_path = Path(directory) / new_name
        if not new_path.exists():
            return new_name
        counter += 1


def get_ffmpeg_installation_guide() -> str:
    """
    Get platform-specific FFmpeg installation instructions.

    Returns:
        Installation guide message for the current platform
    """
    system = platform.system()

    if system == "Windows":
        return """
FFmpeg is not installed or not found in your system PATH.

📦 Installation Options for Windows:

1. Using Chocolatey (Recommended):
   choco install ffmpeg

2. Using Scoop:
   scoop install ffmpeg

3. Manual Installation:
   - Download from: https://www.gyan.dev/ffmpeg/builds/
   - Extract the archive
   - Add the 'bin' folder to your system PATH

After installation, restart your terminal and try again.
"""
    elif system == "Darwin":  # macOS
        return """
FFmpeg is not installed or not found in your system PATH.

📦 Installation for macOS:

Using Homebrew (Recommended):
   brew install ffmpeg

After installation, restart your terminal and try again.
"""
    else:  # Linux and others
        return """
FFmpeg is not installed or not found in your system PATH.

📦 Installation for Linux:

Ubuntu/Debian:
   sudo apt update
   sudo apt install ffmpeg

Fedora:
   sudo dnf install ffmpeg

Arch Linux:
   sudo pacman -S ffmpeg

After installation, restart your terminal and try again.
"""


def check_ffmpeg_available() -> None:
    """
    Check if FFmpeg is available in the system.

    Raises:
        FFmpegNotFoundError: If FFmpeg is not found with installation instructions
    """
    ffmpeg_path = get_ffmpeg_path()

    # Check if ffmpeg is available
    if shutil.which(ffmpeg_path) is None:
        installation_guide = get_ffmpeg_installation_guide()
        raise FFmpegNotFoundError(
            f"FFmpeg is required for video/audio downloads but was not found.{installation_guide}"
        )


def get_ffmpeg_path() -> str:
    """
    Determines the path to the FFmpeg binary.

    If the application is running as a PyInstaller frozen executable,
    it points to the FFmpeg binary bundled with it. Otherwise, it
    defaults to 'ffmpeg', assuming it's in the system's PATH.

    Returns:
        The path to the FFmpeg binary or just 'ffmpeg'.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running in a PyInstaller bundle
        if os.name == "nt":
            ffmpeg_exe = "ffmpeg.exe"
        else:
            ffmpeg_exe = "ffmpeg"

        # The executable is in the same directory as the main app executable
        bundle_dir = os.path.dirname(sys.executable)
        return os.path.join(bundle_dir, ffmpeg_exe)

    # Not running in a bundle (e.g., development environment)
    return "ffmpeg"
