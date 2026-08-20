@echo off
setlocal EnableExtensions
title Arthur optional wake-word setup
cd /d %~dp0
echo.
echo Arthur can install optional local wake-word listening.
echo This setup will create a local Python environment and run:
echo     pip install openwakeword sounddevice
echo It does not send microphone audio to Arthur's cloud providers.
echo.
choice /C YN /N /M "Do you approve this installation"
if errorlevel 2 (
  echo Installation cancelled. No package was installed.
  exit /b 0
)
echo.
if not exist .venv (
  py -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install openwakeword sounddevice
if %errorlevel% neq 0 (
  echo Wake-word installation failed. Check Python and microphone permissions.
  pause
  exit /b 1
)
echo openWakeWord is installed for Arthur.
echo Enable the wake word only after selecting a verified model, granting microphone permission, and completing Arthur's calibration check.
echo Closing Arthur hides it to the system tray only when background mode is enabled. Choosing Exit Arthur stops the listener.
pause
