@echo off
REM Stops any SCORDAGOL dev server (only the process listening on port 5578).
title SCORDAGOL - stop server
set "FOUND="
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5578 " ^| findstr LISTENING') do (
    echo Stopping server PID %%a ...
    taskkill /F /PID %%a >nul 2>&1
    set "FOUND=1"
)
if not defined FOUND (
    echo No server was running on port 5578. Nothing to clean up.
) else (
    echo Done.
)
timeout /t 2 >nul
