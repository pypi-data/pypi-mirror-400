# Deployment script for youtube-search-mcp (Windows PowerShell)
# Usage: .\scripts\deploy.ps1 [-Test]

param(
    [switch]$Test
)

# Colors
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  YouTube Search MCP Deployment Script " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Clean old builds
Write-Host "🧹 Cleaning old builds..." -ForegroundColor Yellow
Remove-Item -Recurse -Force dist, build, src\*.egg-info -ErrorAction SilentlyContinue
Write-Host "✓ Cleaned" -ForegroundColor Green
Write-Host ""

# Step 2: Run tests
Write-Host "🧪 Running tests..." -ForegroundColor Yellow
$testResult = uv run pytest
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Tests failed! Aborting deployment." -ForegroundColor Red
    exit 1
}
Write-Host "✓ All tests passed" -ForegroundColor Green
Write-Host ""

# Step 3: Code quality checks
Write-Host "🔍 Running code quality checks..." -ForegroundColor Yellow

Write-Host "  - Formatting (black)..."
uv run black . --check
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Code not formatted! Run: uv run black ." -ForegroundColor Red
    exit 1
}

Write-Host "  - Linting (ruff)..."
uv run ruff check .
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Linting errors found!" -ForegroundColor Red
    exit 1
}

Write-Host "  - Type checking (mypy)..."
uv run mypy .
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Type checking failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Code quality checks passed" -ForegroundColor Green
Write-Host ""

# Step 4: Build package
Write-Host "📦 Building package..." -ForegroundColor Yellow
uv run python -m build
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Package built successfully" -ForegroundColor Green
Write-Host ""

# Step 5: Upload to PyPI or TestPyPI
if ($Test) {
    Write-Host "🚀 Uploading to TestPyPI..." -ForegroundColor Yellow
    twine upload --repository testpypi dist\*
    Write-Host "✓ Uploaded to TestPyPI" -ForegroundColor Green
    Write-Host ""
    Write-Host "📥 Test installation:" -ForegroundColor Cyan
    Write-Host "   pip install --index-url https://test.pypi.org/simple/ youtube-search-mcp"
} else {
    Write-Host "🚀 Uploading to PyPI..." -ForegroundColor Yellow
    $confirmation = Read-Host "Are you sure you want to upload to PyPI? (y/N)"
    if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
        twine upload dist\*
        Write-Host "✓ Uploaded to PyPI" -ForegroundColor Green
        Write-Host ""
        Write-Host "📥 Installation:" -ForegroundColor Cyan
        Write-Host "   pip install youtube-search-mcp"
    } else {
        Write-Host "Deployment cancelled." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
