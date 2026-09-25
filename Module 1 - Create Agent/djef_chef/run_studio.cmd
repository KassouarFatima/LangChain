@echo off
title DJEF Chef - LangGraph Studio
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
rem --- Load LangSmith secrets from .env so the Studio server reports tracing enabled ---
if exist ".env" (
  for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
    if /i "%%a"=="LANGSMITH_API_KEY" set "LANGSMITH_API_KEY=%%~b"
    if /i "%%a"=="LANGSMITH_TRACING" set "LANGSMITH_TRACING=%%~b"
  )
)
echo.
echo  Starting DJEF Chef LangGraph Studio dev server...
echo  A browser tab will open (or use the printed Studio link).
echo  You will see the graph: model - tools - model.
echo  Send a message like "I have chickpeas, tomatoes, onion, and cumin."
echo  Stop the server by closing this window (Ctrl+C also works).
echo.
uv run langgraph dev
pause