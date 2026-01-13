"""Centralized logging setup for YouTube Search MCP."""

import logging
import sys
from typing import Literal


def setup_logging(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO",
    log_format: str | None = None,
) -> logging.Logger:
    """
    Setup centralized logging configuration.

    IMPORTANT: For MCP servers using STDIO transport, all logs must go to stderr
    because stdout is reserved for JSON-RPC communication.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_format: Optional custom log format

    Returns:
        Configured logger instance
    """
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Force stderr to UTF-8 on Windows to support emojis
    if sys.platform == "win32" and hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            # Fallback if reconfiguration fails (e.g., inside some IDEs or test runners)
            pass

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level),
        format=log_format,
        handlers=[logging.StreamHandler(sys.stderr)],  # MCP requires stderr for logs
    )

    # Get logger for this application
    logger = logging.getLogger("youtube_search_mcp")
    logger.setLevel(getattr(logging, level))

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Get logger instance for a module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    if name is None:
        return logging.getLogger("youtube_search_mcp")
    return logging.getLogger(f"youtube_search_mcp.{name}")
