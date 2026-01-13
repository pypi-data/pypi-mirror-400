# YouTube Search & Download MCP Server 프로젝트 컨텍스트

이 문서는 Gemini가 이 프로젝트를 이해하고 작업하기 위한 핵심 정보를 담고 있습니다. `CLAUDE.md`와 `DEPLOYMENT.md`를 기반으로 작성되었습니다.

## 1. 프로젝트 개요
**YouTube Search & Download MCP Server**는 Model Context Protocol (MCP) 표준을 준수하는 서버로, YouTube API 키 없이 동영상 검색 및 다운로드 기능을 제공합니다.
*   **프레임워크**: FastMCP 2.0
*   **핵심 엔진**: yt-dlp (YouTube 데이터 추출 및 다운로드 담당)
*   **특징**: API Key 불필요, 비디오/오디오 다운로드 지원, 검색 기능 제공.

## 2. 기술 스택 및 환경
*   **언어**: Python 3.10+
*   **패키지 관리**: `uv` (권장) 또는 `pip`
*   **주요 라이브러리**:
    *   `fastmcp`: MCP 서버 구현
    *   `yt-dlp`: YouTube 상호작용
    *   `pydantic`: 데이터 검증 및 설정 관리
    *   `ffmpeg`: 미디어 변환 및 병합 (시스템 PATH에 필수)
*   **개발 도구**:
    *   포맷팅: `black`
    *   린팅: `ruff`
    *   타입 체크: `mypy` (Strict 모드)
    *   테스트: `pytest`, `pytest-asyncio`, `pytest-mock`

## 3. 아키텍처 및 디자인 패턴
이 프로젝트는 **SOLID 원칙**을 엄격히 준수하며 계층화된 아키텍처를 가집니다.

### 핵심 구조 (`src/youtube_search_mcp/`)
*   **Core Abstractions (`core/`)**:
    *   `interfaces.py`: `SearchProvider`, `Downloader`, `ResultFormatter` 등 추상 인터페이스 정의 (DIP 준수).
    *   `config.py`: Pydantic 기반 설정 관리.
*   **Dependency Injection**:
    *   `tools/dependencies.py`: 싱글톤 인스턴스 초기화 및 의존성 주입 컨테이너 역할.
*   **Implementations**:
    *   `search/ytdlp_provider.py`: `yt-dlp`를 이용한 검색 구현.
    *   `download/ytdlp_downloader.py`: 다운로드 로직 구현.
    *   `formatters/`: JSON, Markdown 등 출력 형식 구현 (Strategy 패턴).
*   **MCP Tools (`tools/`)**: FastMCP 도구 등록 및 진입점 (`search_tools.py`, `download_tools.py` 등).

### 주요 디자인 패턴
1.  **Dependency Inversion (의존성 역전)**: 구체적인 구현이 아닌 인터페이스에 의존.
2.  **Singleton (싱글톤)**: 설정 및 서비스 인스턴스 재사용.
3.  **Strategy (전략)**: 포맷터 등을 교체 가능하게 설계.
4.  **Factory (팩토리)**: 조건에 맞는 포맷터 생성.

## 4. 개발 워크플로우

### 설치 및 실행
```bash
# 의존성 설치
uv sync

# 개발 모드 실행
uv run python -m src.youtube_search_mcp.main
# 또는
youtube-search-mcp
```

### 코드 품질 관리
```bash
# 포맷팅, 린팅, 타입 체크 일괄 수행
uv run black . && uv run ruff check . && uv run mypy .
```

### 테스트
```bash
# 전체 테스트 (커버리지 포함)
uv run pytest

# 단위 테스트만 실행
uv run pytest tests/unit
```

## 5. 배포 가이드 (PyPI)
이 프로젝트는 PyInstaller를 사용하여 단일 실행 파일로 컴파일하지 않으며, **PyPI를 통한 패키지 배포**를 원칙으로 합니다.

### 배포 절차
1.  **준비**: 코드 품질 검사 통과 (`pytest`, `black`, `ruff`, `mypy`).
2.  **버전 업**: `pyproject.toml` 버전 수정.
3.  **빌드**:
    ```bash
    uv run python -m build
    ```
    `dist/` 폴더에 `.whl` 및 `.tar.gz` 생성됨.
4.  **배포**:
    ```bash
    twine upload dist/*
    ```

## 6. 설정 (Configuration)
`.env` 파일 또는 환경 변수(`YT_MCP_` 접두사)로 설정 가능합니다.

*   `YT_MCP_DOWNLOAD_DIR`: 다운로드 경로 (기본값: 사용자 홈/Downloads/youtube-mcp)
*   `YT_MCP_DEFAULT_VIDEO_QUALITY`: `best` (기본), `high`, `medium`, `low`
*   `YT_MCP_LOG_LEVEL`: `INFO` (기본)
*   `YT_MCP_MAX_RESULTS`: 검색 결과 수 제한 (기본: 10)

## 7. Gemini 작업 지침
*   **파일 수정 시**: 기존 코드 스타일(Type Hinting, Docstring)과 아키텍처(인터페이스 분리)를 유지하십시오.
*   **기능 추가 시**: 반드시 테스트 코드를 작성하고 로컬에서 검증하십시오.
*   **배포 관련**: 프로젝트 원칙(PyPI 배포)을 상기시키고 가이드를 따르십시오.