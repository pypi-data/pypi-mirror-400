<div align="center">
  <img src="assets/logo.png" alt="Logo" width="200">
  <h1 align="center">YouTube Search & Download MCP Server</h1>
  <p align="center">
    <strong>YouTube API 키 없이 동영상을 검색하고 다운로드하는 MCP 서버</strong>
    <br />
    <a href="https://github.com/easyhak/youtube-search-mcp/issues/new/choose">Bug Report</a>
    ·
    <a href="https://github.com/easyhak/youtube-search-mcp/issues/new/choose">Feature Request</a>
  </p>

  <p align="center">
    <a href="/LICENSE"><img src="https://img.shields.io/github/license/easyhak/youtube-search-mcp?style=flat-square&color=blue" alt="License"></a>
    <a href="https://github.com/easyhak/youtube-search-mcp/releases"><img src="https://img.shields.io/github/v/release/JIHAK-dev/youtube-search-mcp?style=flat-square&color=success" alt="Release"></a>
    <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="Code style: black"></a>
    <a href="https://docs.astral.sh/ruff/"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=flat-square" alt="Ruff"></a>
  </p>

  <p align="center">
    <a href="README.md"><strong>English</strong></a>
    ·
    <a href="README_ko.md"><strong>한국어</strong></a>
  </p>
</div>

---

## 🚀 What is YouTube Search MCP?

This is a production-quality **Model Context Protocol (MCP)** server that allows you to search, get information about, and download YouTube videos and audio without needing a YouTube API key. It's designed to work seamlessly with MCP clients like Claude Desktop and Cursor.

The server is built with `/` for robust backend operations and `FastMCP` for a high-performance server framework.

## ✨ Key Features

-   **No API Key Required**: Search and download freely using `yt-dlp`.
-   **Easy Installation**: Simple setup with `uv` or `pip`. Works seamlessly with MCP clients.
-   **Video & Audio Downloads**: Download content in various formats (`mp4`, `mkv`, `mp3`, `wav`, etc.) and qualities.
-   **Playlist Support**: Search for playlists, get playlist details, and retrieve all videos from any playlist.
-   **Rich Metadata**: Get detailed video information, including duration, view count, and chapters.
-   **Client Compatibility**: Works great with Claude, Cursor, and other MCP-compliant clients.
-   **Robust & Type-Safe**: Built on a SOLID architecture with full type safety using Pydantic.

## 🏁 Getting Started (For Users)

### Prerequisites

-   Python 3.10 or higher
-   [uv](https://docs.astral.sh/uv/) (recommended) or `pip`
-   **FFmpeg** (must be installed and available in your system's PATH)
    -   **Windows**: `choco install ffmpeg` (with Chocolatey) or download from [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/)
    -   **macOS**: `brew install ffmpeg`
    -   **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo dnf install ffmpeg` (Fedora)

### Installation

Install the package using `uv` (recommended) or `pip`:

```bash
# Using uv (recommended)
uv pip install youtube-search-mcp

# Or using pip
pip install youtube-search-mcp
```

### Running the Server

After installation, you can run the server directly:

```bash
youtube-search-mcp
```

## 💻 Client Configuration

Configure your MCP client to connect to the server.

**For Claude Desktop or Cursor:**

Add this to your MCP client configuration (usually `claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "youtube-search": {
      "command": "youtube-search-mcp"
    }
  }
}
```

Or if using `uvx` (no installation required):
```json
{
  "mcpServers": {
    "youtube-search": {
      "command": "uvx",
      "args": ["youtube-search-mcp"]
    }
  }
}
```

## 🔧 Configuration

You can customize the server's behavior by setting environment variables. These can be added to your MCP client configuration (e.g., `claude_desktop_config.json`) or set via a `.env` file in the project root.

| Variable | Description | Default |
|----------|-------------|---------|
| `YT_MCP_DOWNLOAD_DIR` | Directory where videos/audio will be saved | `downloads` |
| `YT_MCP_DEFAULT_VIDEO_QUALITY` | Default video quality (`best`, `high`, `medium`, `low`) | `best` |
| `YT_MCP_DEFAULT_MAX_RESULTS` | Number of search results to return by default | `10` |
| `YT_MCP_LOG_LEVEL` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` |

---


## 🛠️ For Developers & Contributors

Interested in contributing? Here’s how to set up your development environment.

### Prerequisites

-   Git
-   Python 3.10+
-   [uv](https://docs.astral.sh/uv/) (recommended) or `pip`
-   **FFmpeg** (must be installed and available in your system's PATH for development)
    -   **Windows**: `choco install ffmpeg` (with Chocolatey) or download from [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/)
    -   **macOS**: `brew install ffmpeg`
    -   **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or `sudo dnf install ffmpeg` (Fedora)

### Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/JIHAK-dev/youtube-search-mcp.git
    cd youtube-search-mcp
    ```

2.  **Install Dependencies**
    Using `uv` (recommended):
    ```bash
    uv sync
    ```
    Using `pip`:
    ```bash
    python -m venv .venv
    # Activate the virtual environment
    # Windows: .venv\Scripts\activate
    # macOS/Linux: source .venv/bin/activate
    pip install -e ".[dev]"
    ```

3.  **Run the Server**
    Using `uv`:
    ```bash
    uv run python -m youtube_search_mcp.main
    ```
    Or with activated virtual environment:
    ```bash
    python -m youtube_search_mcp.main
    ```

### Code Quality & Testing

-   **Format Code**: `uv run black .`
-   **Lint Code**: `uv run ruff check .`
-   **Type Check**: `uv run mypy .`
-   **Run Tests**: `uv run pytest`

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

Please refer to the [**Contributing Guidelines**](https://github.com/JIHAK-dev/youtube-search-mcp/blob/main/CONTRIBUTING.md) for more details.

## 📜 License

Distributed under the MIT License. See [LICENSE](/LICENSE) for more information.
