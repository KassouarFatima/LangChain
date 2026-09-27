@echo off
title Module 3 - 3_0 Break it first (by Kassouar Fatima 🇩🇿)
cd /d "%~dp0"
set "PATH=C:\Users\Kassouar Fatima\lca-lc-foundations\.venv\Scripts;%PATH%"
set PYTHONIOENCODING=utf-8
echo.
echo  Starting Jupyter Lab - 3_0 Break it first (the Module 3 pre-work)...
echo  A browser tab will open on this notebook; press Run - Run All Cells.
echo  Kernel: lca-lc-foundations\.venv (the only venv with mcp + langchain-mcp-adapters)
echo  Keys load from the wedding project .env (GOOGLE_API_KEY) - about 6 minutes.
echo  Stop the server with Ctrl+C in this window.
echo.
"C:\Users\Kassouar Fatima\lca-lc-foundations\.venv\Scripts\python.exe" -m jupyter lab 3_0_Break_it_first_kassouar.ipynb --port 8898
pause
