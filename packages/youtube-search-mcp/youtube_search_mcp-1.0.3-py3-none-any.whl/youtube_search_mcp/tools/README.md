# MCP Tools Directory

This directory contains all MCP tool implementations, organized by functionality.

## Structure

```
tools/
├── __init__.py              # Package initialization
├── dependencies.py          # Dependency injection container
├── search_tools.py         # Search-related tools
├── playlist_tools.py       # Playlist-related tools
├── download_tools.py       # Download-related tools
├── utility_tools.py        # Utility tools
└── resources.py            # MCP resources
```

## Modules

### dependencies.py
Manages dependency injection for all tools. Provides:
- `initialize_dependencies()`: Initialize all service dependencies
- `get_search_provider()`: Get SearchProvider instance
- `get_downloader()`: Get Downloader instance
- `get_formatter(format_type)`: Get ResultFormatter instance

### search_tools.py
Search-related MCP tools:
- `search_videos`: Search YouTube for videos
- `get_video_info`: Get detailed video information

### playlist_tools.py
Playlist-related MCP tools:
- `search_playlists`: Search for YouTube playlists
- `get_playlist_info`: Get detailed playlist information
- `get_playlist_videos`: List all videos in a playlist

### download_tools.py
Download-related MCP tools:
- `download_video`: Download YouTube videos
- `download_audio`: Download audio from YouTube videos

### utility_tools.py
Utility MCP tools:
- `validate_provider`: Validate search provider is operational

### resources.py
MCP resources:
- `config://current`: Get current server configuration

## Usage

Tools are automatically registered by the main server in [server.py](../server.py):

```python
from .tools.dependencies import initialize_dependencies
from .tools.search_tools import register_search_tools
from .tools.playlist_tools import register_playlist_tools
from .tools.download_tools import register_download_tools
from .tools.utility_tools import register_utility_tools
from .tools.resources import register_resources

# Initialize dependencies
await initialize_dependencies()

# Register all tools
register_search_tools(mcp)
register_playlist_tools(mcp)
register_download_tools(mcp)
register_utility_tools(mcp)
register_resources(mcp)
```

## Adding New Tools

To add a new tool:

1. Create a new file in `tools/` (e.g., `new_tools.py`)
2. Implement a `register_*_tools(mcp: FastMCP)` function
3. Define your tool functions with the `@mcp.tool()` decorator
4. Import and call your registration function in [server.py](../server.py)

Example:

```python
# tools/new_tools.py
from fastmcp import FastMCP

def register_new_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def my_new_tool(param: str) -> str:
        """Tool description."""
        return f"Result: {param}"
```

```python
# server.py
from .tools.new_tools import register_new_tools

register_new_tools(mcp)
```