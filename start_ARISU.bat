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

echo Starting ARISU Services in background...
:: Start Ollama hidden
start "" /B ollama serve > nul 2>&1

:: Start API silently
start "" .\venv_arisu\Scripts\pythonw.exe ARISU_api.py

:: Start Reflector silently
start "" .\venv_arisu\Scripts\pythonw.exe reflector.py

timeout /t 5 /nobreak > nul
echo Services are running silently.
echo.

echo Launching ARISU Interface...
start "" "C:\Users\abril\Documents\VibeCoding\ChatbotAI\ARISU_Interface_v2.hta"

echo.
echo ARISU System Initialized.
timeout /t 2 > nul
exit
