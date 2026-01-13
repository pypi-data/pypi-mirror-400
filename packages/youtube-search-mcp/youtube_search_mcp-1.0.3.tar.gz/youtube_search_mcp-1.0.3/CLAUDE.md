# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server that enables YouTube video search and download functionality without requiring a YouTube API key. It's built with **FastMCP 2.0** framework and uses **yt-dlp** as the underlying engine for YouTube operations.

## Development Commands

### Setup
```bash
# Install dependencies (recommended method)
uv sync

# Or using pip
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
```

### Running the Server
```bash
# Development mode with uv
uv run python -m youtube_search_mcp.server

# Or if venv is activated
python -m youtube_search_mcp.server

# Installed command (after pip/uv installation)
youtube-search-mcp
```

### Code Quality
```bash
# Format code (line-length: 100)
uv run black .

# Lint code
uv run ruff check .

# Type checking (strict mode enabled)
uv run mypy .

# Run all quality checks before committing
uv run black . && uv run ruff check . && uv run mypy .
```

### Testing
```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_search.py

# Run integration tests only
uv run pytest tests/integration/

# Run with verbose output
uv run pytest -v

# Run without coverage report
uv run pytest --no-cov
```

## Architecture Overview

This project follows **SOLID principles** with a layered architecture:

### Core Abstractions (`src/youtube_search_mcp/core/`)
- **`interfaces.py`**: Defines abstract base classes for dependency inversion
  - `SearchProvider`: Abstract interface for search operations
  - `Downloader`: Abstract interface for download operations
  - `ResultFormatter`: Abstract interface for output formatting
  - `ConfigProvider`: Protocol for configuration access
- **`config.py`**: Pydantic-based configuration with environment variable support (prefix: `YT_MCP_`)
- **`exceptions.py`**: Custom exception hierarchy for error handling

### Dependency Injection Pattern
- **`tools/dependencies.py`**: Central dependency container
  - Initializes singleton instances of `SearchProvider`, `Downloader`, and formatters
  - Provides getter functions: `get_search_provider()`, `get_downloader()`, `get_formatter()`
  - Dependencies are initialized once at server startup in `server.py`

### Implementation Layer
- **`search/ytdlp_provider.py`**: Implements `SearchProvider` using yt-dlp
- **`download/ytdlp_downloader.py`**: Implements `Downloader` using yt-dlp
- **`formatters/`**: JSON and Markdown formatters for output

### Data Models (`src/youtube_search_mcp/models/`)
- **`video.py`**: `Video` (basic info) and `VideoDetails` (extended metadata)
- **`search_params.py`**: `SearchParams` for search queries
- **`download_params.py`**: `DownloadParams` and `DownloadResult` for downloads

### MCP Tools Registration (`src/youtube_search_mcp/tools/`)
Tools are registered with FastMCP in separate modules:
- **`search_tools.py`**: `search_videos()`, `get_video_info()`
- **`download_tools.py`**: `download_video()`, `download_audio()`
- **`utility_tools.py`**: Validation and utility functions
- **`resources.py`**: MCP resource registration

### Server Entry Point (`src/youtube_search_mcp/server.py`)
1. Loads configuration from environment/`.env` file
2. Initializes FastMCP server instance
3. Calls `initialize_dependencies()` to set up singletons
4. Registers all tools and resources
5. Runs server with stdio transport

## Configuration

Configuration uses **Pydantic Settings** with `.env` file support. All settings can be overridden with environment variables using the `YT_MCP_` prefix:

```env
YT_MCP_DOWNLOAD_DIR=C:\Users\YourName\Downloads\youtube-mcp
YT_MCP_DEFAULT_VIDEO_QUALITY=best  # best, high, medium, low
YT_MCP_DEFAULT_AUDIO_QUALITY=best
YT_MCP_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
YT_MCP_DEFAULT_MAX_RESULTS=10
YT_MCP_SEARCH_TIMEOUT=30
```

The `download_dir` setting supports environment variable expansion (`%USERPROFILE%`, `$HOME`, `~`).

## External Dependencies

- **FFmpeg** is required at runtime for video/audio processing (must be in system PATH)
- **yt-dlp** handles all YouTube interactions (no API key needed)
- **FastMCP 2.0+** provides the MCP server framework

## Testing Structure

- **`tests/unit/`**: Unit tests for individual components
- **`tests/integration/`**: Integration tests with real yt-dlp operations
- **`tests/fixtures/`**: Shared test fixtures and mock data

Tests use `pytest` with async support (`pytest-asyncio`) and mocking (`pytest-mock`).

## Key Design Patterns

1. **Dependency Inversion**: High-level modules depend on abstractions (interfaces), not concrete implementations
2. **Singleton Pattern**: Configuration and service instances are initialized once and reused
3. **Strategy Pattern**: Different formatters (JSON, Markdown) implement the same interface
4. **Factory Pattern**: `get_formatter()` returns appropriate formatter based on type

## Adding New Features

### To add a new MCP tool:
1. Create the tool function in the appropriate module in `tools/`
2. Use the `@mcp.tool()` decorator from FastMCP
3. Register it in the corresponding `register_*_tools()` function
4. Use dependency injection via `get_search_provider()`, `get_downloader()`, etc.

### To add a new output format:
1. Create a new formatter class implementing `ResultFormatter` interface
2. Add it to the `_formatters` dict in `tools/dependencies.py`

### To support a new video source (beyond YouTube):
1. Create a new class implementing `SearchProvider` and/or `Downloader`
2. Update `initialize_dependencies()` to instantiate your new provider
3. Consider adding configuration options to select providers
