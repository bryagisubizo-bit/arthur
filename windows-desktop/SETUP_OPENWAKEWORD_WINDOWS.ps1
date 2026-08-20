# Arthur local wake-word setup for a source-based Windows installation.
# This script installs only the local wake-word runtime and downloads official
# openWakeWord sample models. It never opens the microphone, starts listening,
# enables background operation, or sends microphone audio anywhere.

[CmdletBinding()]
param(
    [string]$ArthurFolder = (Split-Path -Parent $MyInvocation.MyCommand.Path)
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$python = Join-Path $ArthurFolder ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Arthur's virtual environment was not found at $python. Run the source setup first: py -m venv .venv"
}

Write-Host "Installing local openWakeWord and microphone dependencies into Arthur's virtual environment..."
& $python -m pip install --upgrade pip
& $python -m pip install --upgrade "openwakeword>=0.6,<1" "sounddevice>=0.5,<1"

Write-Host "Downloading official openWakeWord example models. No microphone is opened during this step..."
& $python -c "import openwakeword; openwakeword.utils.download_models(); print('Official model download completed.')"
if ($LASTEXITCODE -ne 0) {
    throw "The official model download did not complete. Check your internet connection and run this script again."
}

$modelRoot = & $python -c "import openwakeword, pathlib; print(pathlib.Path(openwakeword.__file__).parent / 'resources' / 'models')"
Write-Host "Available local model files:"
Get-ChildItem -Path $modelRoot -File | Where-Object { $_.Extension -in ".onnx", ".tflite" } | Select-Object Name, FullName

Write-Host ""
Write-Host "Next: open Arthur > Voice studio > Choose model, then select a verified .onnx model on Windows."
Write-Host "The official example models do not create an Arthur wake word. For ‘Arthur’, select a separately reviewed Arthur .onnx model when you have one."
Write-Host "Finally run Check microphone readiness and explicitly enable the listener in Arthur."
