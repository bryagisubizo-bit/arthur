$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot

if (-not (Get-Command py.exe -ErrorAction SilentlyContinue)) {
    Write-Host "Python Launcher (py.exe) was not found. Install Python 3.12 for Windows, then run this script again." -ForegroundColor Red
    exit 1
}

Write-Host "Starting Arthur's reviewed Windows build workflow..." -ForegroundColor Cyan
& cmd.exe /c build_windows.bat
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Host "Arthur's build did not complete. Review the output above; do not distribute an incomplete installer." -ForegroundColor Red
    exit $exitCode
}

exit 0
