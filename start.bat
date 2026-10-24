@echo off
setlocal
cd /d "%~dp0"
title Opportunity - local preview

python -c "import sys" >nul 2>nul
if not errorlevel 1 (
    python start.py %*
    goto done
)

py -3 -c "import sys" >nul 2>nul
if not errorlevel 1 (
    py -3 start.py %*
    goto done
)

echo.
echo   Python not found.
echo   You can still open index.html directly by double-clicking it.
echo.
pause

:done
endlocal
