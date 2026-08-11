$ErrorActionPreference = "Stop"

$ROOT_DIR = Split-Path -Parent $PSScriptRoot
$SERVER_DIR = Join-Path $ROOT_DIR "server_django"
$CLIENT_DIR = Join-Path $ROOT_DIR "client"
$PYTHON_EXE = Join-Path $SERVER_DIR ".venv\Scripts\python.exe"

if (-not (Test-Path $PYTHON_EXE)) {
    $PYTHON_EXE = "python"
}

function Run-Step {
    param (
        [string]$Name,
        [scriptblock]$Command
    )

    Write-Host ""
    Write-Host "==> $Name" -ForegroundColor Cyan

    & $Command

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR en: $Name" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

Run-Step "Backend - Black" {
    Push-Location $SERVER_DIR
    & $PYTHON_EXE -m black --check apps config tests
    Pop-Location
}

Run-Step "Backend - Pylint" {
    Push-Location $SERVER_DIR
    & $PYTHON_EXE -m pylint apps config tests
    Pop-Location
}

Run-Step "Backend - Mypy" {
    Push-Location $SERVER_DIR
    & $PYTHON_EXE -m mypy apps config
    Pop-Location
}

Run-Step "Backend - Pytest + Coverage" {
    Push-Location $SERVER_DIR
    & $PYTHON_EXE -m coverage run -m pytest
    if ($LASTEXITCODE -eq 0) {
        & $PYTHON_EXE -m coverage report
    }
    Pop-Location
}

Run-Step "Frontend - ESLint" {
    Push-Location $CLIENT_DIR
    pnpm lint
    Pop-Location
}

Run-Step "Frontend - Tests" {
    Push-Location $CLIENT_DIR
    pnpm test
    Pop-Location
}

Run-Step "Frontend - Build" {
    Push-Location $CLIENT_DIR
    pnpm build
    Pop-Location
}

Run-Step "Docker Compose - Config" {
    Push-Location $ROOT_DIR
    docker compose config
    Pop-Location
}

Write-Host ""
Write-Host "Todas las validaciones locales pasaron correctamente." -ForegroundColor Green