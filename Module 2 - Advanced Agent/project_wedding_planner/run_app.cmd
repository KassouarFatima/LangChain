@echo off
title DJEF Wedding - App
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
echo.
echo  Starting DJEF Wedding (Streamlit, blue and white)...
echo  A browser tab will open on http://localhost:8511
echo  Fill the sidebar (guests, wilaya, style, date),
echo  type a request, then press "Prepare the plan".
echo  Stop the app with Ctrl+C in this window.
echo.
REM ---- direct connection: open the playlist database before the app --------
echo  Connecting the playlist database (direct connection)...
"C:\Users\Kassouar Fatima\Downloads\courses\Personal Algerian Chef\.venv\Scripts\python.exe" -c "import sys; sys.path.insert(0, 'notebooks'); import wedding_planner_service as wp; info = wp.ensure_playlist_db(); print('  [DB] direct connection OK ->', info['path']); print('  [DB] tracks in the database:', info['tracks'], '| created just now:', info['created'])"
echo.
"C:\Users\Kassouar Fatima\Downloads\courses\Personal Algerian Chef\.venv\Scripts\python.exe" -m streamlit run streamlit\app.py --server.port 8511
pause
