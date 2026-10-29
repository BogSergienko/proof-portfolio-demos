@echo off
chcp 65001>nul
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (py -3 proof_check.py & goto done)
where python >nul 2>nul
if not errorlevel 1 (python proof_check.py & goto done)
echo Python was not found. Please install Python and retry.
:done
echo.
pause
