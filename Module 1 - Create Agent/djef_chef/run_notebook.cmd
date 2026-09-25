@echo off
title DJEF Chef - Notebook
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo.
echo  Starting DJEF Chef notebook...
echo  A browser tab will open. Then open the folder "notebook"
echo  and double-click DJEF_Chef.ipynb, press Run - Run All Cells.
echo.
uv run jupyter lab --port 8890
pause