"""FastMCP server implementation for YouTube search and download."""

import asyncio

from fastmcp import FastMCP

try:
    from youtube_search_mcp.core.config import get_config
    from youtube_search_mcp.tools.dependencies import initialize_dependencies
    from youtube_search_mcp.tools.download_tools import register_download_tools
    from youtube_search_mcp.tools.playlist_tools import register_playlist_tools
    from youtube_search_mcp.tools.resources import register_resources
    from youtube_search_mcp.tools.search_tools import register_search_tools
    from youtube_search_mcp.tools.utility_tools import register_utility_tools
    from youtube_search_mcp.utils.logger import get_logger, setup_logging
except ImportError:
    from .core.config import get_config
    from .tools.dependencies import initialize_dependencies
    from .tools.download_tools import register_download_tools
    from .tools.playlist_tools import register_playlist_tools
    from .tools.resources import register_resources
    from .tools.search_tools import register_search_tools
    from .tools.utility_tools import register_utility_tools
    from .utils.logger import setup_logging

# Initialize configuration
config = get_config()

# Setup logging
logger = setup_logging(config.log_level)

# Initialize MCP server
mcp = FastMCP(name=config.server_name)

# Register all tools and resources
register_search_tools(mcp)
register_playlist_tools(mcp)
register_download_tools(mcp)
register_utility_tools(mcp)
register_resources(mcp)

# Log registered tools for debugging
try:
    tool_names = list(mcp._tool_manager._tools.keys()) if hasattr(mcp, "_tool_manager") else "unknown"
    logger.info(f"Registered tools: {tool_names}")
except Exception as e:
    logger.warning(f"Failed to log registered tools: {e}")


async def main() -> None:
    """Async entry point for the server."""
    # Initialize dependencies (validates connection)
    await initialize_dependencies()
    
    # Run the server
    logger.info(f"Starting MCP server {config.server_name}")
    await mcp.run_async(transport="stdio")


def run() -> None:
    """Run the MCP server."""
    # Windows-specific workaround for WinError 10014 in asyncio.Runner
    import sys
    
    if sys.platform == "win32":
        try:
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
        except Exception as e:
            logger.error(f"Failed to run server with workaround: {e}")
            # Fallback
            asyncio.run(main())
    else:
        asyncio.run(main())


if __name__ == "__main__":
    run()
