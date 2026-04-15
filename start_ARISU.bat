@echo off
cd /d "%~dp0"
title ARISU Launcher

echo ==========================================
echo        Starting ARISU System
echo ==========================================
echo.

echo Starting Ollama...
start "" /B ollama serve
timeout /t 3 /nobreak > nul
echo Ollama is running!
echo.

echo Starting ARISU API...
start "" /B python ARISU_api.py
timeout /t 2 /nobreak > nul
echo API is running!
echo.

echo Launching ARISU Interface...
start "" "C:\Users\abril\Documents\VibeCoding\ChatbotAI\ARISU.hta"

echo.
echo ARISU is now active.
echo Close this window to stop the system.
pause

echo.
echo Stopping Ollama...
taskkill /IM ollama.exe /F > nul 2>&1
taskkill /IM python.exe /F > nul 2>&1
echo System stopped.