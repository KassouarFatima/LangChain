@echo off
title Module 2 - Advanced Agent - Notebook
cd /d "%~dp0notebooks"
set PYTHONIOENCODING=utf-8
echo.
echo  Starting Module 2 notebook (lesson 2.1 - MCP)...
echo  A browser tab will open. Open 2_1_MCP_kassouar.ipynb,
echo  then press Run - Run All Cells. Kernel: Python (djef).
echo.
"C:\Users\Kassouar Fatima\Downloads\courses\Personal Algerian Chef\.venv\Scripts\python.exe" -m jupyter lab --port 8891
pause