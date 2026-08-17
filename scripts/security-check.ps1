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

$rawSqlMatches = Get-ChildItem -Path $ServerDir -Recurse -File -Include *.py |
    Where-Object {
        $_.FullName -notmatch "\\.venv\\" -and
        $_.FullName -notmatch "\\migrations\\" -and
        $_.FullName -notmatch "\\__pycache__\\"
    } |
    Select-String -Pattern "RawSQL|\.raw\(|\.extra\(|connection\.cursor|cursor\.execute|\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b"

if ($rawSqlMatches) {
    $rawSqlMatches
    throw "Potential raw SQL usage found. Review the matches above."
}

Write-Host "No raw SQL patterns found in project code." -ForegroundColor Green

Write-Step "Security - Django deploy check"

Push-Location $ServerDir
& $PythonExe manage.py check --deploy
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
