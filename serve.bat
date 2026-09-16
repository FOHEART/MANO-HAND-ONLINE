@echo off
REM ============================================================
REM  One-click dev server for MANO HAND ONLINE (Windows).
REM  Double-click this file, or run:  serve.bat --port 9000
REM ============================================================
setlocal
cd /d "%~dp0"

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"

if not defined PY (
    echo.
    echo   Python 3 was not found on PATH.
    echo   Install it from https://www.python.org/downloads/
    echo   and tick "Add python.exe to PATH", then try again.
    echo.
    pause
    exit /b 1
)

%PY% serve.py %*
echo.
pause
