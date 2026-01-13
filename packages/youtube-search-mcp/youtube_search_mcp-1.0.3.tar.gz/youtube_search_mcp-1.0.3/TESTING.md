# MCP 서버 테스트 가이드

개발 중인 YouTube Search MCP 서버를 테스트하는 방법을 설명합니다.
---

## 📋 테스트 방법 3가지

1. **Claude Desktop 연결** (가장 추천! 실제 사용 환경)
2. **MCP Inspector** (웹 기반 GUI 테스트)
3. **단위 테스트** (자동화된 코드 테스트)

---

## 🎯 방법 1: Claude Desktop에서 테스트 (추천)

실제 사용 환경에서 직접 테스트하는 가장 확실한 방법입니다.

### Step 1: 개발 모드로 서버 실행 확인

터미널에서 서버가 정상 실행되는지 확인:

```bash
# 프로젝트 디렉토리에서
uv run python -m youtube_search_mcp.server
```

서버가 시작되면 입력 대기 상태가 됩니다. (아무것도 출력 안 될 수 있음 - 정상입니다)
`Ctrl+C`로 종료하세요.

### Step 2: Claude Desktop 설정

Claude Desktop 설정 파일을 엽니다:

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### Step 3: 개발 버전 설정 추가

설정 파일에 다음을 추가:

```json
{
  "mcpServers": {
    "youtube-search-dev": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\Projects\\youtube_search_mcp",
        "python",
        "-m",
        "youtube_search_mcp.server"
      ],
      "env": {
        "YT_MCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

**중요:** `C:\\Projects\\youtube_search_mcp`를 실제 프로젝트 경로로 변경하세요!

**macOS/Linux 경로 예시:**
```json
{
  "mcpServers": {
    "youtube-search-dev": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/yourname/Projects/youtube_search_mcp",
        "python",
        "-m",
        "youtube_search_mcp.server"
      ],
      "env": {
        "YT_MCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Step 4: Claude Desktop 재시작

1. Claude Desktop을 **완전히 종료** (작업 표시줄/메뉴바에서도 종료)
2. Claude Desktop을 다시 실행
3. 새 대화 시작

### Step 5: 테스트!

Claude에서 다음과 같이 요청해보세요:

```
사용 가능한 도구를 보여줘
```

```
"Python tutorial" 영상을 검색해줘
```

```
이 영상 정보를 알려줘: dQw4w9WgXcQ
```

### 로그 확인

문제가 발생하면 로그를 확인하세요:

**Windows:**
```
%APPDATA%\Claude\logs
```

**macOS:**
```
~/Library/Logs/Claude
```

가장 최근 로그 파일에서 `youtube-search-dev` 관련 오류를 찾으세요.

---

## 🌐 방법 2: MCP Inspector (웹 기반)

FastMCP에 Inspector 기능이 있는 경우 사용할 수 있습니다.

### Step 1: Inspector 모드로 서버 실행

`server.py`를 임시로 수정하거나 별도 스크립트를 만듭니다:

**`test_inspector.py` 생성:**

```python
"""MCP Inspector 테스트용 스크립트"""

from youtube_search_mcp.server import mcp

if __name__ == "__main__":
    # SSE transport로 실행 (Inspector 사용)
    mcp.run(transport="sse")
```

### Step 2: Inspector 실행

```bash
uv run python test_inspector.py
```

서버가 시작되면 웹 브라우저에서 주소가 표시됩니다 (예: `http://localhost:8000`).

### Step 3: 웹 브라우저에서 테스트

브라우저에서 GUI를 통해 도구를 호출하고 결과를 확인할 수 있습니다.

**참고:** FastMCP 버전에 따라 지원되지 않을 수 있습니다.

---

## 🧪 방법 3: 단위 테스트 (자동화)

기존 pytest 테스트를 실행합니다.

### 모든 테스트 실행

```bash
uv run pytest
```

### 특정 테스트만 실행

```bash
# 검색 기능 테스트
uv run pytest tests/unit/test_search.py -v

# 다운로드 기능 테스트
uv run pytest tests/unit/test_download.py -v

# 통합 테스트
uv run pytest tests/integration/ -v
```

### 커버리지 없이 빠르게 실행

```bash
uv run pytest --no-cov -v
```

### 특정 테스트 케이스만 실행

```bash
uv run pytest tests/unit/test_search.py::test_search_videos -v
```

---

## 🔧 수동 테스트 (고급)

MCP 프로토콜을 직접 테스트하려면 JSON-RPC 메시지를 보낼 수 있습니다.

### Step 1: 서버 실행

```bash
uv run python -m youtube_search_mcp.server
```

### Step 2: JSON-RPC 메시지 입력

서버는 stdin으로 JSON-RPC 메시지를 받습니다. 예시:

**초기화 요청:**
```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}
```

**도구 목록 요청:**
```json
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
```

**검색 실행:**
```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"search_videos","arguments":{"query":"python tutorial","max_results":3}}}
```

매우 번거로우므로 **Claude Desktop 연결 방법을 추천**합니다!

---

## ✅ 테스트 체크리스트

개발 후 다음을 확인하세요:

### 기능 테스트
- [ ] `search_videos` - 검색이 정상 작동하는가?
- [ ] `get_video_info` - 비디오 정보 조회가 되는가?
- [ ] `download_video` - 비디오 다운로드가 되는가?
- [ ] `download_audio` - 오디오 다운로드가 되는가?
- [ ] `validate_provider` - yt-dlp 연결이 확인되는가?

### 오류 처리
- [ ] 잘못된 비디오 ID 입력 시 적절한 오류 메시지
- [ ] 네트워크 오류 시 재시도 동작
- [ ] 존재하지 않는 비디오 처리
- [ ] 디스크 공간 부족 시 오류 처리

### 성능
- [ ] 검색 속도가 적절한가? (5초 이내)
- [ ] 다운로드가 정상 속도로 진행되는가?
- [ ] 동시 요청 처리가 되는가?

### 품질
- [ ] 모든 pytest 테스트 통과
- [ ] Black 포맷팅 준수
- [ ] Ruff 린팅 통과
- [ ] MyPy 타입 체크 통과

---

## 🐛 일반적인 문제 해결

### Claude Desktop에서 도구가 안 보임

**확인 사항:**
1. Claude Desktop을 완전히 재시작했는지
2. JSON 문법이 올바른지 (쉼표, 중괄호)
3. 경로가 정확한지 (`\\`로 구분 - Windows)
4. 로그에 오류가 있는지

**디버깅:**
```bash
# 서버가 직접 실행되는지 확인
uv run python -m youtube_search_mcp.server

# 의존성이 설치되었는지 확인
uv sync
```

### Import 오류

```bash
# 의존성 재설치
uv sync

# 캐시 정리 후 재설치
rm -rf .venv
uv sync
```

### yt-dlp 오류

```bash
# yt-dlp 업데이트
uv pip install --upgrade yt-dlp
```

---

## 📊 추천 테스트 순서

1. **pytest 실행** - 코드가 기본적으로 작동하는지 확인
   ```bash
   uv run pytest
   ```

2. **직접 실행 테스트** - 서버가 시작되는지 확인
   ```bash
   uv run python -m youtube_search_mcp.server
   ```

3. **Claude Desktop 연결** - 실제 환경에서 테스트
   - 설정 파일 수정
   - Claude 재시작
   - 도구 사용해보기

4. **코드 수정 시** - 변경사항 반영
   - Claude Desktop 재시작 (서버 재로드됨)
   - 다시 테스트

---

## 💡 개발 팁

### 빠른 반복 개발

코드 수정 → Claude Desktop 재시작 → 테스트 → 반복

**자동화 스크립트 (선택사항):**

**Windows PowerShell:**
```powershell
# kill-claude-restart.ps1
Get-Process Claude -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
Start-Process "C:\Users\YourName\AppData\Local\Programs\Claude\Claude.exe"
```

**macOS/Linux:**
```bash
# restart-claude.sh
killall Claude
sleep 2
open -a "Claude"
```

### 로그 레벨 조정

개발 중에는 DEBUG 레벨로 설정:

```json
{
  "mcpServers": {
    "youtube-search-dev": {
      "command": "uv",
      "args": ["..."],
      "env": {
        "YT_MCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

---

## 🎉 테스트 완료!

모든 기능이 잘 작동하면 배포 준비가 된 것입니다!

다음 단계: [DEPLOYMENT.md](./DEPLOYMENT.md) 참조
