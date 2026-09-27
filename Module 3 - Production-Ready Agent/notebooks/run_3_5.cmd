@echo off
title Module 3 - 3_5 Email agent (by Kassouar Fatima 🇩🇿)
cd /d "%~dp0"
set "PATH=C:\Users\Kassouar Fatima\lca-lc-foundations\.venv\Scripts;%PATH%"
set PYTHONIOENCODING=utf-8
echo.
echo  Starting Jupyter Lab - 3_5 Email agent (auth + inbox + approval door)...
echo  A browser tab will open on this notebook; press Run - Run All Cells.
echo  Kernel: lca-lc-foundations\.venv (the course venv: langchain v1 + langgraph)
echo  Keys load from the .env next to this notebook (GOOGLE_API_KEY) - about a minute.
echo  Stop the server with Ctrl+C in this window.
echo.
"C:\Users\Kassouar Fatima\lca-lc-foundations\.venv\Scripts\python.exe" -m jupyter lab 3_5_Email_agent_kassouar.ipynb --port 8903
pause
