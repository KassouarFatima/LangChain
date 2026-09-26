@echo off
title DJEF Wedding - Notebook
cd /d "%~dp0notebooks"
set PYTHONIOENCODING=utf-8
echo.
echo  Starting DJEF Wedding notebook...
echo  A browser tab will open. Open wedding_planner_kassouar.ipynb,
echo  then press Run - Run All Cells. Kernel: Python (djef).
echo  The key loads from the .env of this project automatically.
echo.
"C:\Users\Kassouar Fatima\Downloads\courses\Personal Algerian Chef\.venv\Scripts\python.exe" -m jupyter lab --port 8892
pause
