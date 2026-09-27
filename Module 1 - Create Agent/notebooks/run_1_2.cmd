@echo off
title Module 1 - Lesson 1_2 (notebook)
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo.
echo  Starting Jupyter Lab - lesson 1_2: Tools and web search...
echo  A browser tab will open on this notebook; press Run - Run All Cells.
echo  Kernel: djef_chef\.venv (Python 3.13) - keys load from djef_chef\.env
echo  (TAVILY_API_KEY needed for the web search tool)
echo  Stop the server with Ctrl+C in this window.
echo.
"%~dp0..\djef_chef\.venv\Scripts\python.exe" -X utf8 -c "import os,sys,subprocess,pathlib;from dotenv import load_dotenv;here=pathlib.Path(r'%~dp0.').resolve();proj=here.parent/'djef_chef';load_dotenv(proj/'.env',override=True);os.environ.setdefault('GOOGLE_API_KEY',os.environ.get('GEMINI_API_KEY',''));os.environ['PATH']=str(proj/'.venv'/'Scripts')+os.pathsep+os.environ['PATH'];sys.exit(subprocess.call([sys.executable,'-m','jupyter','lab','1_2_Tools_and_web_search_kassouar.ipynb','--port','8893'],cwd=str(here)))"
pause
