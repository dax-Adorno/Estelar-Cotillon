$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)

    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

$RootDir = Split-Path -Parent $PSScriptRoot
$ServerDir = Join-Path $RootDir "server_django"
$ClientDir = Join-Path $RootDir "client"
$PythonExe = Join-Path $ServerDir ".venv\Scripts\python.exe"
$RequirementsFile = Join-Path $ServerDir "requirements.txt"

Write-Step "Security - Raw SQL search"

$rawSqlPatterns = @(
    "RawSQL",
    "\.raw\(",
    "\.extra\(",
    "connection\.cursor",
    "cursor\.execute",
    '["'']\s*(SELECT|INSERT|UPDATE|DELETE)\s+'
)

$rawSqlMatches = Get-ChildItem -Path $ServerDir -Recurse -File -Include *.py |
    Where-Object {
        $_.FullName -notmatch "\\.venv\\" -and
        $_.FullName -notmatch "\\migrations\\" -and
        $_.FullName -notmatch "\\__pycache__\\"
    } |
    Select-String -Pattern $rawSqlPatterns

if ($rawSqlMatches) {
    $rawSqlMatches
    throw "Potential raw SQL usage found. Review the matches above."
}

Write-Host "No raw SQL patterns found in project code." -ForegroundColor Green

Write-Step "Security - Django deploy check"

$env:DJANGO_DEBUG = "False"
$env:DJANGO_SECRET_KEY = "security-check-only-7f4a2b8d1c6e9a3f5b0d8c2e7a4f1b6d9c3e5a8f"
$env:DJANGO_ALLOWED_HOSTS = "tienda.example.com"
$env:CORS_ALLOWED_ORIGINS = "https://tienda.example.com"
$env:CSRF_TRUSTED_ORIGINS = "https://tienda.example.com"
$env:FRONTEND_URL = "https://tienda.example.com"
$env:DATABASE_ENGINE = "postgres"
$env:POSTGRES_DB = "estelart_db"
$env:POSTGRES_USER = "estelart_user"
$env:POSTGRES_PASSWORD = "security-check-only-password"
$env:DJANGO_SECURE_SSL_REDIRECT = "True"
$env:DJANGO_SESSION_COOKIE_SECURE = "True"
$env:DJANGO_CSRF_COOKIE_SECURE = "True"
$env:DJANGO_SECURE_HSTS_SECONDS = "31536000"
$env:DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS = "True"
$env:DJANGO_SECURE_HSTS_PRELOAD = "True"

Push-Location $ServerDir
& $PythonExe manage.py check --deploy --fail-level WARNING
if ($LASTEXITCODE -ne 0) {
    Pop-Location
    throw "Django deploy check failed."
}
Pop-Location

Write-Step "Security - pip-audit"

& $PythonExe -m pip_audit -r $RequirementsFile
if ($LASTEXITCODE -ne 0) {
    throw "pip-audit found issues or is not installed."
}

Write-Step "Security - pnpm audit"

Push-Location $ClientDir
pnpm audit
if ($LASTEXITCODE -ne 0) {
    Pop-Location
    throw "pnpm audit found issues."
}
Pop-Location

Write-Host ""
Write-Host "Security checks completed." -ForegroundColor Green
