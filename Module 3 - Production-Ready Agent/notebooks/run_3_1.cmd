@echo off
title Module 3 - 3_1 Where your agent needs a door (by Kassouar Fatima 🇩🇿)
cd /d "%~dp0"
set "PATH=C:\Users\Kassouar Fatima\lca-lc-foundations\.venv\Scripts;%PATH%"
set PYTHONIOENCODING=utf-8
echo.
echo  Starting Jupyter Lab - 3_1 Where your agent needs a door...
echo  A browser tab will open on this notebook; press Run - Run All Cells.
echo  Kernel: lca-lc-foundations\.venv (this notebook never calls the model)
echo  No API key needed - a few seconds. Run 3_0 first: 3_1 audits its answers file.
echo  Stop the server with Ctrl+C in this window.
echo.
"C:\Users\Kassouar Fatima\lca-lc-foundations\.venv\Scripts\python.exe" -m jupyter lab 3_1_Where_your_agent_needs_a_door_kassouar.ipynb --port 8899
pause
