@echo off
cd /d "%~dp0"
title UtilityHub Converter Setup
echo Installing yt-dlp...
python -m pip install --upgrade yt-dlp
if errorlevel 1 (echo Failed to install yt-dlp. & pause & exit /b 1)
echo.
echo Checking FFmpeg...
where ffmpeg >nul 2>&1
if errorlevel 1 (
 echo FFmpeg is not on PATH. Install it with: winget install --id Gyan.FFmpeg -e
 echo Then RESTART VS Code and UtilityHub.
) else (echo FFmpeg is available.)
echo.
pause
