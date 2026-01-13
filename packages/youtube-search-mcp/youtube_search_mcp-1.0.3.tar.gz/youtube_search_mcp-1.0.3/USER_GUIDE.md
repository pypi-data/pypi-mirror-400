# User Guide / 사용자 가이드

This guide explains how to install, configure, and use the YouTube Search & Download MCP Server.
이 가이드는 YouTube Search & Download MCP 서버의 설치, 설정 및 사용 방법을 설명합니다.

- [English Guide](#english-guide)
- [한국어 가이드](#korean-guide)

---

<a id="english-guide"></a>
## 🇬🇧 English Guide

### 🚀 Quick Install

#### 1. Prerequisites

- **Python 3.10+**: Required to run the server.
- **FFmpeg**: Required for video/audio processing and merging.

#### 2. Install FFmpeg

**Windows:**
```powershell
choco install ffmpeg
# Or download from https://ffmpeg.org/download.html and add to PATH
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

#### 3. Install MCP Server

You can install it using `pip` or `uv` (recommended).

```bash
# Using pip
pip install youtube-search-mcp

# Using uv (Recommended)
uv pip install youtube-search-mcp
```

### ⚙️ Configuration (Claude Desktop / Cursor)

#### Configuration File Locations

**Claude Desktop:**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Cursor:**
- Windows: `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`
- macOS: `~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

#### Add to Configuration

Open the configuration file and add the following JSON:

```json
{
  "mcpServers": {
    "youtube-search": {
      "command": "youtube-search-mcp"
    }
  }
}
```

**If you have other MCP servers:**

```json
{
  "mcpServers": {
    "other-server": {
      "command": "other-command"
    },
    "youtube-search": {
      "command": "youtube-search-mcp"
    }
  }
}
```

#### Apply Changes

1. **Quit** Claude Desktop or Cursor completely.
2. Restart the application.
3. Start a new conversation.

### 💡 Usage Examples

You can use natural language to interact with the tools.

#### Search Videos
> "Find 5 videos about 'Python tutorials'."

#### Get Video Info
> "Get info for this video: https://www.youtube.com/watch?v=dQw4w9WgXcQ"

#### Download Video
> "Download this video in high quality: dQw4w9WgXcQ"

- **Quality options**: `best`, `high`, `medium`, `low`

#### Download Audio
> "Extract audio from this video as MP3: dQw4w9WgXcQ"

- **Format options**: `mp3`, `m4a`, `opus`, `wav`

### 🔧 Advanced Configuration

Most users do not need to configure anything. However, if you wish to customize the server's behavior, you can use environment variables.

| Variable | Description | Default |
|---|---|---|
| `YT_MCP_DOWNLOAD_DIR` | Directory for downloaded files | `downloads` |
| `YT_MCP_DEFAULT_VIDEO_QUALITY` | Default video quality (`best`, `high`, etc.) | `best` |
| `YT_MCP_DEFAULT_MAX_RESULTS` | Default number of search results | `10` |
| `YT_MCP_LOG_LEVEL` | Log level (`DEBUG`, `INFO`, etc.) | `INFO` |

Below is an example of how to set them in your MCP client's configuration file:

```json
{
  "mcpServers": {
    "youtube-search": {
      "command": "youtube-search-mcp",
      "env": {
        "YT_MCP_DOWNLOAD_DIR": "C:\\Users\\YourName\\Downloads\\YouTube",
        "YT_MCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### 🐛 Troubleshooting

#### "command not found" Error

If the `youtube-search-mcp` command is not recognized, specify the full path to your Python executable and the module.

```json
{
  "mcpServers": {
    "youtube-search": {
      "command": "python",
      "args": ["-m", "youtube_search_mcp.main"]
    }
  }
}
```
*Note: Ensure `python` is in your PATH or use the full path to the python executable.*

#### FFmpeg Error

Verify FFmpeg installation in your terminal:
```bash
ffmpeg -version
```
If not installed, refer to the [Install FFmpeg](#2-install-ffmpeg) section.

---

<a id="korean-guide"></a>
## 🇰🇷 한국어 가이드

### 🚀 빠른 설치

#### 1. 사전 준비

- **Python 3.10+**: 서버 실행을 위해 필요합니다.
- **FFmpeg**: 비디오/오디오 처리 및 병합을 위해 필수입니다.

#### 2. FFmpeg 설치

**Windows:**
```powershell
choco install ffmpeg
# 또는 https://ffmpeg.org/download.html 에서 다운로드 후 PATH에 추가
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

#### 3. MCP 서버 설치

`pip` 또는 `uv`(권장)를 사용하여 설치할 수 있습니다.

```bash
# pip 사용
pip install youtube-search-mcp

# uv 사용 (권장)
uv pip install youtube-search-mcp
```

### ⚙️ 설정 (Claude Desktop / Cursor)

#### 설정 파일 위치

**Claude Desktop:**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Cursor:**
- Windows: `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`
- macOS: `~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

#### 설정 추가

해당 설정 파일을 열고 아래 JSON 내용을 추가하세요:

```json
{
  "mcpServers": {
    "youtube-search": {
      "command": "youtube-search-mcp"
    }
  }
}
```

**이미 다른 MCP 서버가 있는 경우:**

```json
{
  "mcpServers": {
    "other-server": {
      "command": "other-command"
    },
    "youtube-search": {
      "command": "youtube-search-mcp"
    }
  }
}
```

#### 적용 방법

1. Claude Desktop 또는 Cursor를 **완전히 종료**합니다.
2. 프로그램을 다시 실행합니다.
3. 새로운 대화를 시작합니다.

### 💡 사용 방법

자연어로 도구 사용을 요청할 수 있습니다.

#### 동영상 검색
> "'파이썬 강좌' 영상 5개 찾아줘"

#### 동영상 정보 조회
> "이 링크의 영상 정보 알려줘: https://www.youtube.com/watch?v=dQw4w9WgXcQ"

#### 동영상 다운로드
> "이 영상을 고화질로 다운로드해줘: dQw4w9WgXcQ"

- **화질 옵션**: `best`, `high`, `medium`, `low`

#### 오디오 다운로드
> "이 영상에서 오디오만 MP3로 추출해줘: dQw4w9WgXcQ"

- **포맷 옵션**: `mp3`, `m4a`, `opus`, `wav`

### 🔧 고급 설정 (선택사항)

대부분의 사용자는 별도의 설정이 필요하지 않습니다. 하지만 필요한 경우 환경 변수를 사용하여 서버의 동작을 변경할 수 있습니다.

| 변수명 | 설명 | 기본값 |
|---|---|---|
| `YT_MCP_DOWNLOAD_DIR` | 다운로드 저장 경로 | `downloads` |
| `YT_MCP_DEFAULT_VIDEO_QUALITY` | 기본 비디오 화질 (`best`, `high` 등) | `best` |
| `YT_MCP_DEFAULT_MAX_RESULTS` | 기본 검색 결과 수 | `10` |
| `YT_MCP_LOG_LEVEL` | 로그 레벨 (`DEBUG`, `INFO` 등) | `INFO` |

아래는 MCP 클라이언트 설정 파일에서 환경 변수를 설정하는 예시입니다.

```json
{
  "mcpServers": {
    "youtube-search": {
      "command": "youtube-search-mcp",
      "env": {
        "YT_MCP_DOWNLOAD_DIR": "C:\\Users\\사용자명\\Downloads\\YouTube",
        "YT_MCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### 🐛 문제 해결

#### "command not found" 오류

`youtube-search-mcp` 명령어를 찾을 수 없는 경우, Python 실행 파일 경로와 모듈을 직접 지정하세요.

```json
{
  "mcpServers": {
    "youtube-search": {
      "command": "python",
      "args": ["-m", "youtube_search_mcp.main"]
    }
  }
}
```
*참고: `python`이 PATH에 등록되어 있거나, Python 실행 파일의 전체 경로를 사용해야 합니다.*

#### FFmpeg 오류

터미널에서 FFmpeg 설치 여부를 확인하세요:
```bash
ffmpeg -version
```
설치되어 있지 않다면 [FFmpeg 설치](#2-ffmpeg-설치) 섹션을 참고하세요.