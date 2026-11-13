@echo off
cd /d "%~dp0"
title UtilityHub Local Server
python main.py
if errorlevel 1 (
  echo.
  echo UtilityHub could not start. Check that Python is installed and port 3000 is available.
  pause
)
