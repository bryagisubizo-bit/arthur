@echo off
setlocal EnableExtensions
cd /d "%~dp0"

where py >nul 2>&1
if errorlevel 1 (
  echo Python Launcher ^(py.exe^) was not found. Install Python 3.12 for Windows, then run this file again.
  goto :finish
)

if not exist ".venv\Scripts\python.exe" (
  py -m venv .venv
  if errorlevel 1 goto :build_failed
)

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if errorlevel 1 goto :build_failed
python -m pip install -r requirements.txt
if errorlevel 1 goto :build_failed

echo Preparing bundled local runtime assets and openWakeWord models ...
python prepare_runtime_assets.py
if errorlevel 1 goto :build_failed

for %%F in (test_*.py) do (
  echo Running %%F ...
  python "%%F"
  if errorlevel 1 (
    echo Arthur regression check failed: %%F
    goto :build_failed
  )
)

echo.
echo Building Arthur.exe with PyInstaller ...
python -m PyInstaller --noconfirm --clean Arthur.spec
if errorlevel 1 goto :build_failed
if not exist "dist\Arthur\Arthur.exe" (
  echo PyInstaller did not produce dist\Arthur\Arthur.exe.
  goto :build_failed
)

set "ISCC="
for %%I in (ISCC.exe) do set "ISCC=%%~$PATH:I"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 7\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 7\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 7\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"

if not defined ISCC (
  echo.
  echo Arthur.exe is ready at dist\Arthur\Arthur.exe.
  echo Inno Setup was not found, so open installer\ArthurSetup.iss and click Compile.
  goto :finish
)

echo.
echo Compiling the installer with Inno Setup ...
"%ISCC%" "installer\ArthurSetup.iss"
if errorlevel 1 goto :build_failed

if exist "installer\output\ArthurSetup-0.1.6.exe" (
  echo.
  echo SUCCESS: installer\output\ArthurSetup-0.1.6.exe is ready to install.
) else (
  echo Inno Setup finished but the expected installer file was not found.
  goto :build_failed
)
goto :finish

:build_failed
echo.
echo Arthur build did not complete. Review the message above; no installer should be distributed.

:finish
pause
