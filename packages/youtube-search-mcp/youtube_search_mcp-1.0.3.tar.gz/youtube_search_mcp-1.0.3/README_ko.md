<div align="center">
  <img src="assets/logo.png" alt="Logo" width="150">
  <h1 align="center">YouTube Search & Download MCP Server</h1>
  <p align="center">
    <strong>YouTube API 키 없이 동영상을 검색하고 다운로드하는 MCP 서버</strong>
    <br />
    <a href="https://github.com/easyhak/youtube-search-mcp/issues/new/choose">버그 리포트</a>
    ·
    <a href="https://github.com/easyhak/youtube-search-mcp/issues/new/choose">기능 요청</a>
  </p>

  <p align="center">
    <a href="/LICENSE"><img src="https://img.shields.io/github/license/easyhak/youtube-search-mcp?style=flat-square&color=blue" alt="License"></a>
    <a href="https://github.com/easyhak/youtube-search-mcp/releases"><img src="https://img.shields.io/github/v/release/easyhak/youtube-search-mcp?style=flat-square&color=success" alt="Release"></a>
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

## 🚀 YouTube Search MCP란?

이 프로젝트는 YouTube API 키 없이 동영상을 검색하고, 정보를 얻고, 다운로드할 수 있는 고품질 **MCP(Model Context Protocol)** 서버입니다. Claude Desktop, Cursor와 같은 MCP 클라이언트와 완벽하게 연동되도록 설계되었습니다.

백엔드에서는 강력한 `yt-dlp`를, 서버 프레임워크로는 고성능 `FastMCP`를 사용하여 제작되었습니다.

## ✨ 주요 특징

-   **API 키 불필요**: `yt-dlp`를 사용하여 자유롭게 검색하고 다운로드하세요.
-   **간편한 설치**: `uv` 또는 `pip`를 통한 간단한 설치. MCP 클라이언트와 완벽하게 연동됩니다.
-   **비디오 및 오디오 다운로드**: 다양한 포맷(`mp4`, `mkv`, `mp3`, `wav` 등)과 화질로 콘텐츠를 다운로드할 수 있습니다.
-   **풍부한 메타데이터**: 영상 길이, 조회수, 챕터 등 상세한 동영상 정보를 얻을 수 있습니다.
-   **클라이언트 호환성**: Claude, Cursor 등 MCP를 지원하는 클라이언트에서 훌륭하게 작동합니다.
-   **견고함과 타입 안정성**: SOLID 원칙에 따라 설계되었으며, Pydantic을 통해 완벽한 타입 안정성을 보장합니다.

## 🏁 시작하기 (일반 사용자용)

### 사전 요구사항

-   Python 3.10 이상
-   [uv](https://docs.astral.sh/uv/) (권장) 또는 `pip`
-   **FFmpeg** (시스템 PATH에 설치되어 있어야 합니다)
    -   **Windows**: `choco install ffmpeg` (Chocolatey 사용) 또는 [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/)에서 다운로드
    -   **macOS**: `brew install ffmpeg`
    -   **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) 또는 `sudo dnf install ffmpeg` (Fedora)

### 설치 방법

`uv` (권장) 또는 `pip`를 사용하여 패키지를 설치하세요:

```bash

# uv 사용 (권장)
uv pip install youtube-search-mcp

# 또는 pip 사용
pip install youtube-search-mcp
```

### 서버 실행

설치 후 서버를 바로 실행할 수 있습니다:

```bash
youtube-search-mcp
```

## 💻 클라이언트 설정

MCP 클라이언트에서 서버에 연결하도록 설정하세요.

**Claude Desktop 또는 Cursor에서 사용:**

MCP 클라이언트 설정(보통 `claude_desktop_config.json`)에 다음을 추가하세요:
```json
{
  "mcpServers": {
    "youtube-search": {
      "command": "youtube-search-mcp"
    }
  }
}
```

또는 `uvx`를 사용하는 경우 (설치 불필요):
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

## 🔧 환경설정

환경 변수를 설정하여 서버의 동작을 변경할 수 있습니다. MCP 클라이언트 설정 파일(`claude_desktop_config.json` 등)에 추가하거나, 프로젝트 루트에 `.env` 파일을 생성하여 설정할 수 있습니다.

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `YT_MCP_DOWNLOAD_DIR` | 비디오/오디오가 저장될 디렉토리 | `downloads` |
| `YT_MCP_DEFAULT_VIDEO_QUALITY` | 기본 비디오 품질 (`best`, `high`, `medium`, `low`) | `best` |
| `YT_MCP_DEFAULT_MAX_RESULTS` | 기본 검색 결과 개수 | `10` |
| `YT_MCP_LOG_LEVEL` | 로그 레벨 (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` |

---


## 🛠️ 개발자 및 기여자를 위해

프로젝트에 기여하고 싶으신가요? 아래 안내에 따라 개발 환경을 설정할 수 있습니다.

### 사전 요구사항

-   Git
-   Python 3.10 이상
-   [uv](https://docs.astral.sh/uv/) (권장) 또는 `pip`
-   **FFmpeg** (개발 환경에서는 시스템 PATH에 설치되어 있어야 합니다)
    -   **Windows**: `choco install ffmpeg` (Chocolatey 사용) 또는 [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/)에서 다운로드
    -   **macOS**: `brew install ffmpeg`
    -   **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) 또는 `sudo dnf install ffmpeg` (Fedora)

### 설정 방법

1.  **리포지토리 클론**
    ```bash
    git clone https://github.com/easyhak/youtube-search-mcp.git
    cd youtube-search-mcp
    ```

2.  **의존성 설치**
    `uv` 사용 시 (권장):
    ```bash
    uv sync
    ```
    `pip` 사용 시:
    ```bash
    python -m venv .venv
    # 가상 환경 활성화
    # Windows: .venv\Scripts\activate
    # macOS/Linux: source .venv/bin/activate
    pip install -e ".[dev]"
    ```

3.  **개발 서버 실행**
    `uv` 사용:
    ```bash
    uv run python -m youtube_search_mcp.main
    ```
    또는 가상 환경 활성화 후:
    ```bash
    python -m youtube_search_mcp.main
    ```

### 코드 품질 및 테스트

-   **코드 포맷팅**: `uv run black .`
-   **코드 린팅**: `uv run ruff check .`
-   **타입 검사**: `uv run mypy .`
-   **테스트 실행**: `uv run pytest`

## 🤝 기여하기

오픈소스 커뮤니티는 여러분의 기여를 통해 성장합니다. 어떤 형태의 기여든 대환영입니다.

자세한 내용은 [**기여 가이드라인**](https://github.com/easyhak/youtube-search-mcp/blob/main/CONTRIBUTING.md)을 참고해 주세요.

## 📜 라이선스

MIT 라이선스에 따라 배포됩니다. 자세한 내용은 [LICENSE](/LICENSE) 파일을 확인하세요.
