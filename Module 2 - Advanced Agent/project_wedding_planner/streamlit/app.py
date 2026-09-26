"""DJEF Travel & Event Planner — small Streamlit app (Module 2 project).

Run it from the project folder with the DJEF environment:

    double-click  run_app.cmd          (recommended — opens http://localhost:8511)

or manually:

    "<djef-python>" -m streamlit run streamlit/app.py --server.port 8511

The code is divided into small parts, one concern per file:

    design.py     — the look (page, header, footer)
    components.py — one widget / button per function
    runner.py     — the functionality (keys, the team, context, saved runs)
    app.py        — only the assembly (this file)

The team itself lives in notebooks/wedding_planner_service.py — one
Coordinator Agent and three specialists (flights via MCP, venues via web
search, playlist via SQL). Theme: blue & white (.streamlit/config.toml).
"""
import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent
for _folder in (_HERE, _HERE.parent / "notebooks"):
    if str(_folder) not in sys.path:
        sys.path.insert(0, str(_folder))

import streamlit as st

import design

design.page_config()  # the first streamlit command on the page
design.theme_css()     # dark-mode overrides (the sidebar switch)

VENV_PY = (
    r"C:\Users\Kassouar Fatima\Downloads\courses"
    r"\Personal Algerian Chef\.venv\Scripts\python.exe"
)

# The DJEF environment is required; Anaconda's Python ships a broken langchain mix.
try:
    import runner
    import components as ui
except ImportError as _exc:
    st.error(
        "**Wrong Python environment (this looks like Anaconda).**\n\n"
        "The app must run with the DJEF environment. Close this page, then "
        "double-click **`run_app.cmd`** in the project folder, or run in a terminal:\n\n"
        "```\n"
        f'"{VENV_PY}" -m streamlit run streamlit/app.py --server.port 8511\n'
        "```\n\n"
        f"Details: `{_exc}`"
    )
    st.stop()

runner.load_keys()
design.header()

ui.sidebar_top()
wedding = ui.sidebar_wedding()
ui.sample_brief_button()
reopened = ui.saved_runs_sidebar()
question = ui.request_box()

shown = None
if ui.prepare_button():
    if not question.strip():
        ui.empty_request_note()
    else:
        try:
            shown = runner.run_plan(question, wedding)
        except Exception as _exc:  # friendly message, no traceback
            ui.service_error(_exc)

if shown is None:
    shown = runner.reopened_text(reopened)

ui.show_plan(shown)
design.footer()
