@echo off
title ClipMind AI Public Web Tunnel
cd /d "%~dp0"

echo ========================================================
echo        Opening Public Web Link for ClipMind AI
echo ========================================================
echo.
echo [*] Ensure ClipMind AI is running in another window (run.bat).
echo [*] Generating instant public HTTPS link...
echo.

npx localtunnel --port 8501
pause
