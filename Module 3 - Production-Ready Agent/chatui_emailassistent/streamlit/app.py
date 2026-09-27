"""DJEF Email Assistant — Streamlit app (Module 3 project).

Professional chat UI combining the Email Assistant agent
(authenticate · check_inbox · send_email with HITL approval).

Covers the full Module 3 brief:
  - Context holds email + password
  - Custom state field tracks authentication
  - Three tools: authenticate, check_inbox, send_email
  - Dynamic tools (only authenticate before auth)
  - Dynamic prompt (doorman vs email assistant)
  - Human-in-the-loop on send (approve / edit / reject)
  - Tool calls can be hidden or shown

Run:  double-click  run_app.cmd  (opens http://localhost:8519)

by Kassouar Fatima 🇩🇿 — Module 3 — Production-Ready Agent.
"""
from __future__ import annotations

import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import streamlit as st

import design
import runner
import components as ui

PYTHON_EXE = r"C:\ProgramData\anaconda3\python.exe"

# ===========================================================================
# First streamlit commands — page config, theme, session state
# ===========================================================================
design.page_config()  # the first streamlit command on the page

# Initialize session state
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = False
if "show_tool_calls" not in st.session_state:
    st.session_state["show_tool_calls"] = False

design.theme_css()    # dark-mode overrides

# ===========================================================================
# Environment check
# ===========================================================================
try:
    import email_agent_service as svc  # noqa: E402
    runner.load_keys()
except ImportError as _exc:  # noqa: E402
    design.hero_banner()
    st.error(
        "**Missing dependencies.**\n\n"
        "The app needs: streamlit, langchain, langgraph, langchain-google-genai,\n"
        "python-dotenv. Install them with:\n\n"
        "```\n"
        f'"{PYTHON_EXE}" -m pip install -r requirements.txt\n'
        "```\n\n"
        f"Details: `{_exc}`"
    )
    st.stop()

# ===========================================================================
# Hero + sidebar + auth
# ===========================================================================
design.hero_banner()
design.sub_header()

# Sidebar
ui.sidebar_top()
auth = ui.sidebar_auth()
ui.sample_request_button()
reopened = ui.saved_runs_sidebar()
ui.tool_calls_toggle()
ui.chat_history()
ui.clear_chat()
ui.show_all_emails_button()

# ===========================================================================
# Re-open a saved run
# ===========================================================================
if reopened and reopened != "(none)":
    for r in st.session_state["runs"]:
        if f"{r['at']}  ·  {r['title']}" == reopened:
            st.session_state["messages"] = [
                {"role": "user", "content": r["title"]},
                {"role": "assistant", "content": r["text"]},
            ]
            st.rerun()

# ===========================================================================
# Session state
# ===========================================================================
st.session_state.setdefault("messages", [])
st.session_state.setdefault("interrupted", False)
st.session_state.setdefault("thread_id", "1")
st.session_state.setdefault("runs", [])

# ===========================================================================
# Show existing messages
# ===========================================================================
def _clean_content(content: str) -> str:
    """Remove the __HITL__: prefix from display content."""
    if content.startswith("__HITL__:"):
        return content.split(":", 1)[1]
    return content


for msg in st.session_state.get("messages", []):
    role = msg["role"]
    content = _clean_content(msg["content"])
    if role == "user":
        st.chat_message("user").markdown(content)
    else:
        st.chat_message("assistant").markdown(content)

# ===========================================================================
# Handle HITL approval flow (pending approval from a previous turn)
# ===========================================================================
if st.session_state.get("interrupted"):
    with st.chat_message("assistant"):
        st.markdown("> ⏸️ **Approval needed** — the assistant wants to send an email.")

        # Get the pending draft from the last HITL message
        pending_body = ""
        for msg in reversed(st.session_state.get("messages", [])):
            if msg["role"] == "assistant" and msg["content"].startswith("__HITL__:"):
                pending_body = msg["content"].split(":", 1)[1]
                break

        # Editable draft + approve / edit / reject buttons
        edited_draft = ui.show_pending_draft(pending_body)
        decision = ui.approve_buttons()

        if decision:
            with st.spinner(f"Processing {decision}…"):
                if decision == "edit":
                    result = runner.resume(
                        decision, st.session_state["thread_id"], edited_draft
                    )
                else:
                    result = runner.resume(
                        decision, st.session_state["thread_id"]
                    )

            if result.startswith("__HITL__:"):
                body = result.split(":", 1)[1]
                st.markdown(f"**Draft:** {body}")
                st.info("⏸️ Approval needed again.")
            else:
                st.markdown(result)
                st.session_state["messages"].append(
                    {"role": "assistant", "content": result}
                )
                st.session_state["interrupted"] = False

# ===========================================================================
# Display all emails if requested
# ===========================================================================
ui.display_all_emails()

# ===========================================================================
# Chat input — send a message
# ===========================================================================
question = ui.chat_box()
if question:
    # Show the user message
    st.chat_message("user").markdown(question)
    st.session_state["messages"].append({"role": "user", "content": question})

    # Run the agent
    with st.chat_message("assistant"):
        try:
            result = runner.run(question, auth, st.session_state["thread_id"])
        except Exception as e:
            result = f"❌ **Error!** 🇩🇿\n\n**Saha,** something went wrong:\n```\n{type(e).__name__}: {e}\n```"

        if result.startswith("__HITL__:"):
            body = result.split(":", 1)[1]
            st.markdown(f"**⏸️ Pending draft:**\n\n{body}")
            st.info("Approval needed — approve, edit, or reject.")
            st.session_state["interrupted"] = True
            st.session_state["messages"].append(
                {"role": "assistant", "content": f"__HITL__:{body}"}
            )
        else:
            st.markdown(result)
            st.session_state["messages"].append(
                {"role": "assistant", "content": result}
            )

# ===========================================================================
# Footer
# ===========================================================================
design.footer()
