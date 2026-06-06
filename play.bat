@echo off
title Volley Challenge - local server
cd /d "%~dp0"
echo ============================================================
echo  Volley Challenge - Anfield Edition
echo ============================================================
echo  Opening http://localhost:5577/index.html in your browser.
echo  KEEP THIS WINDOW OPEN while you play.
echo  Close this window (or press Ctrl+C) to stop the game.
echo ============================================================
REM Free port 5577 first so old servers don't pile up in Task Manager.
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5577 " ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
start "" "http://localhost:5577/index.html?v=%RANDOM%%RANDOM%"
py serve.py 2>nul || python serve.py
