# 배포 가이드 (Deployment Guide)

이 문서는 `youtube-search-mcp` 패키지를 배포하는 방법을 설명합니다.

## 📋 목차

1. [배포 전 체크리스트](#-배포-전-체크리스트)
2. [PyPI 배포 (권장)](#-pypi-배포-권장)
3. [GitHub 릴리스](#-github-릴리스)
4. [버전 관리](#-버전-관리)

---

## ✅ 배포 전 체크리스트

배포하기 전에 다음 항목들을 확인하세요:

### 1. 코드 품질 검사

```bash
# 모든 테스트 통과 확인
uv run pytest

# 코드 포맷팅
uv run black .

# 린팅
uv run ruff check .

# 타입 체크
uv run mypy .
```

### 2. 버전 확인

`pyproject.toml`의 버전이 올바른지 확인하세요:
```toml
[project]
version = "1.0.1"  # 적절한 버전으로 업데이트
```

### 3. 문서 확인

- [ ] README.md가 최신 상태인가?
- [ ] CHANGELOG.md가 업데이트되었나? (있는 경우)
- [ ] 모든 설정 예시가 정확한가?

### 4. Git 상태 확인

```bash
# 모든 변경사항이 커밋되었는지 확인
git status

# 원격 저장소와 동기화
git push origin main
```

---

## 🚀 PyPI 배포 (권장)

### 사전 준비

#### 1. PyPI 계정 생성
- [PyPI](https://pypi.org/) 계정 생성 (없는 경우)
- [TestPyPI](https://test.pypi.org/) 계정 생성 (테스트용)

#### 2. API 토큰 생성
1. PyPI에 로그인
2. Account Settings → API tokens
3. "Add API token" 클릭
4. Scope: "Entire account" (첫 배포) 또는 특정 프로젝트
5. 생성된 토큰을 안전한 곳에 저장

#### 3. 빌드 도구 설치

`uv`를 사용하는 경우 별도의 빌드 도구(`build`) 설치가 필요 없습니다 (`uv build` 내장 명령어 사용).
패키지 업로드 도구인 `twine`만 준비하면 됩니다.

```bash
# uv 도구로 twine 설치 (권장)
uv tool install twine

# 또는 현재 가상환경에 설치
uv pip install twine
```

### 배포 단계

#### Step 1: 빌드 테스트

```bash
# 프로젝트 빌드
uv build

# 또는
python -m build
```

빌드가 완료되면 `dist/` 폴더에 다음 파일들이 생성됩니다:
- `youtube_search_mcp-1.0.1-py3-none-any.whl`
- `youtube_search_mcp-1.0.1.tar.gz`

#### Step 2: 로컬 설치 테스트

```bash
# 빌드된 패키지를 새 가상환경에서 테스트
python -m venv test_env
# Windows
test_env\Scripts\activate
# macOS/Linux
# source test_env/bin/activate

pip install dist/youtube_search_mcp-1.0.1-py3-none-any.whl

# 명령어 실행 테스트
youtube-search-mcp --help

# 테스트 완료 후
deactivate
rm -rf test_env  # 또는 Windows: rmdir /s test_env
```

#### Step 3: TestPyPI에 먼저 배포 (선택사항)

```bash
# TestPyPI에 업로드
uvx twine upload --repository testpypi dist/*

# 프롬프트에서 다음 입력:
# Username: __token__
# Password: [생성한 API 토큰]
```

TestPyPI에서 설치 테스트:
```bash
pip install --index-url https://test.pypi.org/simple/ youtube-search-mcp
```

#### Step 4: 실제 PyPI에 배포

```bash
# PyPI에 업로드
uvx twine upload dist/*
```

#### Step 5: 배포 확인

1. [PyPI 패키지 페이지](https://pypi.org/project/youtube-search-mcp/) 확인
2. 설치 테스트:
   ```bash
   pip install youtube-search-mcp
   youtube-search-mcp --help
   ```

### 배포 자동화 (선택사항)

`.pypirc` 파일을 홈 디렉토리에 생성하여 자동화할 수 있습니다:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-[여기에_실제_토큰]

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-[여기에_TestPyPI_토큰]
```

**⚠️ 주의**: `.pypirc` 파일은 절대 Git에 커밋하지 마세요!

---

## 📌 GitHub 릴리스

### Step 1: Git 태그 생성

```bash
# 현재 버전에 태그 생성
git tag -a v1.0.1 -m "Release version 1.0.1"

# 태그를 원격 저장소에 푸시
git push origin v1.0.1
```

### Step 2: GitHub Release 생성

1. GitHub 저장소 페이지로 이동
2. "Releases" → "Create a new release" 클릭
3. 태그 선택: `v1.0.1`
4. 릴리스 제목: `v1.0.1 - [간단한 설명]`
5. 릴리스 노트 작성:
   ```markdown
   ## What's New
   - 기능 1
   - 기능 2

   ## Bug Fixes
   - 버그 수정 1

   ## Installation
   ```bash
   pip install youtube-search-mcp==1.0.1
   ```
   ```
6. 빌드 파일 첨부 (선택사항):
   - `dist/youtube_search_mcp-1.0.1-py3-none-any.whl`
   - `dist/youtube_search_mcp-1.0.1.tar.gz`
7. "Publish release" 클릭

---

## 🔄 버전 관리

### 유의적 버전(Semantic Versioning)

버전 번호는 `MAJOR.MINOR.PATCH` 형식을 따릅니다:

- **MAJOR** (1.x.x): 하위 호환성이 깨지는 변경
- **MINOR** (x.1.x): 하위 호환성을 유지하는 기능 추가
- **PATCH** (x.x.1): 하위 호환성을 유지하는 버그 수정

### 버전 업데이트 절차

1. **`pyproject.toml` 수정**
   ```toml
   version = "1.0.2"  # 새 버전으로 변경
   ```

2. **CHANGELOG.md 업데이트** (있는 경우)
   ```markdown
   ## [1.0.2] - 2024-01-15
   ### Fixed
   - 버그 수정 내용
   ```

3. **변경사항 커밋**
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Bump version to 1.0.2"
   git push origin main
   ```

4. **새 버전 배포**
   - 위의 PyPI 배포 단계 반복
   - GitHub 릴리스 생성

---

## 🛠️ 배포 스크립트 (선택사항)

배포 과정을 자동화하는 스크립트를 만들 수 있습니다:

**`scripts/deploy.sh`** (macOS/Linux):
```bash
#!/bin/bash
set -e

echo "🧹 Cleaning old builds..."
rm -rf dist/ build/ *.egg-info

echo "🧪 Running tests..."
uv run pytest

echo "📦 Building package..."
uv build

echo "🚀 Uploading to PyPI..."
uvx twine upload dist/*

echo "✅ Deployment complete!"
```

**`scripts/deploy.ps1`** (Windows PowerShell):
```powershell
Write-Host "🧹 Cleaning old builds..." -ForegroundColor Cyan
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue

Write-Host "🧪 Running tests..." -ForegroundColor Cyan
uv run pytest

Write-Host "📦 Building package..." -ForegroundColor Cyan
uv build

Write-Host "🚀 Uploading to PyPI..." -ForegroundColor Cyan
uvx twine upload dist/*

Write-Host "✅ Deployment complete!" -ForegroundColor Green
```

사용법:
```bash
# macOS/Linux
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# Windows
.\scripts\deploy.ps1
```

---

## 📚 추가 리소스

- [PyPI 공식 문서](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine 문서](https://twine.readthedocs.io/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Releases 가이드](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)

---

## 🆘 문제 해결

### "File already exists" 오류
- 이미 해당 버전이 PyPI에 업로드되어 있습니다
- `pyproject.toml`의 버전을 올리고 다시 빌드하세요

### "Invalid distribution" 오류
- `dist/` 폴더를 삭제하고 다시 빌드하세요
- `python -m build --no-isolation` 시도

### Import 오류
- 패키지 구조 확인: `src/youtube_search_mcp/` 폴더에 `__init__.py`가 있는지
- `pyproject.toml`의 `packages` 설정 확인

---

## 📝 체크리스트

배포 전 마지막 확인:

- [ ] 모든 테스트 통과
- [ ] 코드 품질 검사 완료 (black, ruff, mypy)
- [ ] 버전 번호 업데이트
- [ ] README.md 최신화
- [ ] Git 변경사항 모두 커밋 및 푸시
- [ ] 빌드 성공 확인
- [ ] 로컬 설치 테스트 완료
- [ ] TestPyPI 테스트 (선택)
- [ ] PyPI 배포
- [ ] GitHub 릴리스 생성
- [ ] 실제 설치 테스트 (`pip install youtube-search-mcp`)
