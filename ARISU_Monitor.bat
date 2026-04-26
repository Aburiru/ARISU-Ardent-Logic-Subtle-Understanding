@echo off
title ARISU SYSTEM MONITOR
echo ============================================================
echo           ARISU REAL-TIME LOG MONITOR
echo    (Close this window to stop monitoring, services will stay)
echo ============================================================
echo.
powershell -Command "Get-Content -Path 'arisu_debug.log' -Wait -Tail 20"
