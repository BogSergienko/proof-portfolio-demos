@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (py -3 process_orders.py) else (python process_orders.py)
echo.
echo Ready: 01, 02, 03 CSV and 04 JSON.
pause
