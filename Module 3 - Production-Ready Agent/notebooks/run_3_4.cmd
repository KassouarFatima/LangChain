@echo off
title Module 3 - 3_4 Dynamic (by Kassouar Fatima 🇩🇿)
cd /d "%~dp0"
set "PATH=C:\Users\Kassouar Fatima\lca-lc-foundations\.venv\Scripts;%PATH%"
set PYTHONIOENCODING=utf-8
echo.
echo  Starting Jupyter Lab - 3_4 Dynamic models / prompts / tools (all three)...
echo  A browser tab will open with the three notebooks; press Run - Run All Cells.
echo  Kernel: lca-lc-foundations\.venv (the course venv: langchain v1 + langgraph)
echo  Keys load from the .env next to these notebooks (GOOGLE_API_KEY + TAVILY_API_KEY).
echo  The tools notebook reads resources\Chinook.db (shipped next to the notebooks).
echo  Stop the server with Ctrl+C in this window.
echo.
"C:\Users\Kassouar Fatima\lca-lc-foundations\.venv\Scripts\python.exe" -m jupyter lab 3_4_Dynamic_models_kassouar.ipynb 3_4_Dynamic_prompts_kassouar.ipynb 3_4_Dynamic_tools_kassouar.ipynb --port 8902
pause
