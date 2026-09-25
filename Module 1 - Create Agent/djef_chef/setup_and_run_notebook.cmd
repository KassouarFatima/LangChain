@echo off
title DJEF Chef - Setup + Notebook (any Windows machine)
cd /d "%~dp0"
where uv >nul 2>nul
if errorlevel 1 (
    echo.
    echo  uv not found. Installing it with pip (once)...
    python -m pip install --quiet uv
)
echo.
echo  Installing the project packages (first time only, can take a minute)...
uv sync
set PYTHONIOENCODING=utf-8
echo.
echo  Starting DJEF Chef notebook...
echo  A browser tab will open. Then open the folder "notebook"
echo  and double-click DJEF_Chef.ipynb, press Run - Run All Cells.
echo.
uv run jupyter lab --port 8890
pause