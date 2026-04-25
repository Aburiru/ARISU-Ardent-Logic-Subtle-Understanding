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
:: Running in a separate window so you can see if it crashes
start "ARISU API" .\venv_arisu\Scripts\python.exe ARISU_api.py
timeout /t 5 /nobreak > nul
echo API window should be open.
echo.

echo Launching ARISU Interface...
start "" "C:\Users\abril\Documents\VibeCoding\ChatbotAI\ARISU.hta"

echo.
echo ARISU is now active.
echo You can close this launcher window.
echo (The API and Ollama will continue running in the background)
pause
