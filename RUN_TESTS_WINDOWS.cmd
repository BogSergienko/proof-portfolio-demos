@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 -m unittest discover -s tests -v
) else (
  where python >nul 2>nul
  if not errorlevel 1 (
    python -m unittest discover -s tests -v
  ) else (
    echo Python 3 not found. Install Python and retry.
  )
)
echo.
pause
