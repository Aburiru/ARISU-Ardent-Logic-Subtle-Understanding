@echo off
cd /d "%~dp0"
title ARISU Launcher

echo ==========================================
echo        Starting ARISU System
echo ==========================================
echo.

:: Check if Ollama is running, if not start it
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo Starting Ollama...
    start "" /B ollama serve
    timeout /t 3 /nobreak > nul
) else (
    echo Ollama is already running.
)

echo Starting ARISU Services...
:: Start API silently
start "" .\venv_arisu\Scripts\pythonw.exe ARISU_api.py

:: Start Reflector silently
start "" .\venv_arisu\Scripts\pythonw.exe reflector.py

timeout /t 3 /nobreak > nul
echo Services are running.
echo.

echo Launching ARISU Interface...
start "" "C:\Users\abril\Documents\VibeCoding\ChatbotAI\ARISU_Interface_v2.hta"

echo.
echo ARISU System Initialized.
timeout /t 2 > nul
exit
