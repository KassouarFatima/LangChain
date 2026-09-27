@echo off
cd /d "C:\Users\Kassouar Fatima\Downloads\LangChain\Module 3 - Production-Ready Agent\chatui_emailassistent\streamlit"
REM --server.fileWatcherType none : do NOT auto-rerun when a file changes on disk.
REM An external editor/agent saving app.py would otherwise ABORT the script run that
REM is answering your chat, so your typed message stays but the reply never arrives.
"C:\ProgramData\anaconda3\python.exe" -m streamlit run app.py --server.port 8519 --server.fileWatcherType none
