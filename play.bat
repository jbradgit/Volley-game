@echo off
title SCORDAGOL - local server
cd /d "%~dp0"
echo ============================================================
echo  SCORDAGOL - local server
echo ============================================================
echo  The game will open in your browser in a moment.
echo  KEEP THIS WINDOW OPEN while you play.
echo  Close this window (or press Ctrl+C) to stop the game.
echo ============================================================
REM Free the port first so old servers don't pile up.
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5578 " ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
REM Open the browser AFTER a short delay, so the server below is listening first (avoids "refused to connect").
start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://localhost:5578/index.html?v=%RANDOM%%RANDOM%'"
REM Start the server (this blocks and keeps the window open while you play).
py serve.py 2>nul || python serve.py
echo.
echo  Server stopped. If you saw a Python error above, install Python from python.org and run play again.
pause
