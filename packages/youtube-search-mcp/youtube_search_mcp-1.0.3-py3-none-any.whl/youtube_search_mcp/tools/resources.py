"""MCP resources for server information."""

from fastmcp import FastMCP

from ..core.config import get_config


def register_resources(mcp: FastMCP) -> None:
    """
    Register all resources with the MCP server.

    Args:
        mcp: FastMCP server instance
    """

    @mcp.resource("config://current")
    def get_current_config() -> str:
        """
        Get current server configuration.

        Returns:
            Formatted configuration information
        """
        config = get_config()
        return f"""# YouTube Search MCP Configuration

- Server: {config.server_name} v{config.server_version}
- Default max results: {config.default_max_results}
- Max results limit: {config.max_results_limit}
- Search timeout: {config.search_timeout}s
- Max retries: {config.max_retries}
- Download directory: {config.download_dir}
- Default video quality: {config.default_video_quality}
- Default audio quality: {config.default_audio_quality}
- Min disk space: {config.min_disk_space_mb}MB
- Log level: {config.log_level}
- Default format: {config.default_format}
"""
