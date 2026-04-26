@echo off
title ARISU SYSTEM STOP
echo Stopping all ARISU background services...

:: Kill Python processes running the API and Reflector
taskkill /F /IM pythonw.exe /T

:: Optionally stop Ollama if desired (comment out if you want Ollama to stay)
:: taskkill /F /IM ollama.exe /T

echo.
echo ARISU Services Stopped.
timeout /t 2 > nul
