@echo off
title DJEF Chef (Module 1 copy) - App
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo.
echo  Starting DJEF Chef - Module 1 copy (Streamlit)...
echo  A browser tab will open on http://localhost:8502
echo  Stop the app with Ctrl+C in this window.
echo.
"%~dp0.venv\Scripts\python.exe" -m streamlit run streamlit\app.py --server.port 8502
pause
