"""Widgets of the DJEF Email Assistant app — one function per widget/button.

Professional sidebar with branded DJEF logo, auth section,
theme toggle, sample request, saved runs, and styled chat + approval buttons.

by Kassouar Fatima 🇩🇿 — Module 3 — Production-Ready Agent.
"""
from __future__ import annotations

import streamlit as st

import runner

SAMPLE_REQUEST = (
    "kassouarfatima@gmail.com, password123\n\n"
    "Please check my inbox and reply: I'll be there, bring the coffee."
)


# ---------------------------------------------------------------------------
# Sidebar — branded DJEF navigation
# ---------------------------------------------------------------------------
def sidebar_top() -> None:
    """Branded sidebar header with logo, name, and theme toggle."""
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; margin-bottom:1rem;">
                <div style="
                    font-size: 2.5rem;
                    margin-bottom: 0.2rem;
                ">🇩🇿</div>
                <div style="
                    font-size: 1.3rem;
                    font-weight: 800;
                    color: #d49a32;
                    letter-spacing: 2px;
                ">DJEF</div>
                <div style="
                    font-size: 0.85rem;
                    color: #f5fbf8;
                    opacity: 0.8;
                    margin-top: 0.1rem;
                ">Email Assistant</div>
                <div style="
                    margin-top: 0.5rem;
                    font-size: 0.75rem;
                    color: #cfe6db;
                ">by Kassouar Fatima 🇩🇿</div>
            </div>
            <hr style="border-color: rgba(255,255,255,0.15); margin-bottom:1rem;">
            """,
            unsafe_allow_html=True,
        )
        _theme_toggle()
        st.divider()


def _theme_toggle() -> None:
    """Dark mode only."""
    st.button("🌙 Dark mode", key="sidebar_theme_toggle", use_container_width=True, disabled=True)


def sidebar_auth() -> dict:
    """Authentication section in the sidebar."""
    with st.sidebar:
        st.header("🔐 Authenticate", divider="green")
        email = st.text_input(
            "Email",
            value="kassouarfatima@gmail.com",
            help="Context — the assistant's known address",
        )
        password = st.text_input(
            "Password",
            type="password",
            value="password123",
            help="Context — the assistant's known password",
        )
        # Mail transport status — lives here (not in app.py) so it renders
        # with the auth block no matter how app.py is regenerated.
        mail_mode_status()
    return {"email": email, "password": password}


def mail_mode_status() -> None:
    """Sidebar line: is the app talking to real Gmail or the built-in store?"""
    with st.sidebar:
        st.divider()
        kind, summary = runner.mail_status()
        if kind == "real":
            st.success(f"📧 {summary}")
        elif kind == "blocked":
            st.error(f"🛑 {summary}")
        else:
            st.info(
                f"📬 {summary}\n\n"
                "Set `EMAIL_PASSWORD` in `.env` to a Gmail **App Password** "
                "to go live."
            )


def sample_request_button() -> None:
    """Button: fill the chat with a ready-made request."""
    with st.sidebar:
        st.divider()
        if st.button("📋 Load sample request", use_container_width=True):
            st.session_state["chat_input"] = SAMPLE_REQUEST
            st.rerun()


def saved_runs_sidebar() -> str | None:
    """Sidebar list of this session's runs."""
    with st.sidebar:
        st.divider()
        st.markdown("**💾 Sessions**")
        runs = st.session_state.get("runs", [])
        if runs:
            return st.selectbox(
                "Reopen a session",
                ["(none)"] + [f"{r['at']}  ·  {r['title']}" for r in runs],
                key="reopen_select",
            )
        st.caption("No conversations yet.")
    return "(none)"


def tool_calls_toggle() -> None:
    """Toggle to show or hide tool calls in the chat."""
    with st.sidebar:
        st.divider()
        show_tools = st.toggle(
            "🔧  Show tool calls",
            value=bool(st.session_state.get("show_tool_calls", False)),
            help="Display tool calls (authenticate, check_inbox, send_email) in the chat",
        )
        st.session_state["show_tool_calls"] = show_tools


def chat_history() -> None:
    """Display the conversation history in the sidebar."""
    with st.sidebar:
        st.divider()
        st.markdown("**💬 Chat History**")
        messages = st.session_state.get("messages", [])
        if not messages:
            st.caption("No messages yet.")
        else:
            for msg in reversed(messages):
                role = msg["role"]
                content = msg["content"]
                if content.startswith("__HITL__:"):
                    content = content.split(":", 1)[1][:50] + "…"
                if role == "user":
                    st.markdown(f"👤 **You**: {content[:80]}{'…' if len(content) > 80 else ''}")
                else:
                    st.markdown(f"🤖 **Assistant**: {content[:80]}{'…' if len(content) > 80 else ''}")


def clear_chat() -> None:
    """Button to clear the chat history."""
    with st.sidebar:
        st.divider()
        if st.button("🗑️  Clear chat", use_container_width=True):
            st.session_state["messages"] = []
            st.session_state["runs"] = []
            st.session_state["interrupted"] = False
            st.rerun()


def show_all_emails_button() -> None:
    """Sidebar button to display all sent/received emails."""
    with st.sidebar:
        st.divider()
        if st.button("📬  Show all emails", use_container_width=True):
            st.session_state["show_email_list"] = True
            st.rerun()


def display_all_emails() -> None:
    """Show all emails in the chat area if the toggle is active."""
    if st.session_state.get("show_email_list"):
        st.markdown("### 📬 All Emails — Sent & Received 📬")
        import runner
        emails_text = runner.get_all_emails_text()
        st.text(emails_text)
        st.markdown("---")
        if st.button("✖️ Hide email list", key="hide_email_list"):
            st.session_state["show_email_list"] = False
            st.rerun()


# ---------------------------------------------------------------------------
# Chat area
# ---------------------------------------------------------------------------
def chat_box() -> str | None:
    """The chat input box (filled by the sample request button)."""
    return st.chat_input(
        placeholder="Type a message… e.g. kassouarfatima@gmail.com, password123 — then check inbox or send email",
        key="chat_input",
    )


def approve_buttons() -> str | None:
    """Approve / Edit / Reject buttons when the agent is waiting for HITL approval.

    Returns "approve", "edit", "reject", or None.
    """
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✅  Approve", type="primary", use_container_width=True):
            return "approve"
    with col2:
        if st.button("✏️  Edit", use_container_width=True):
            return "edit"
    with col3:
        if st.button("❌  Reject", use_container_width=True):
            return "reject"
    return None


def show_pending_draft(body: str) -> str:
    """Show the pending email draft with an editable text area.

    Returns the (possibly edited) draft text.
    """
    st.markdown("> ⏸️ **Approval needed** — the assistant wants to send this email:")
    edited = st.text_area(
        "Draft (editable)",
        value=body,
        height=150,
        key="draft_editor",
        help="Edit the draft, then approve, edit again, or reject",
    )
    st.info("Approve to send, edit to change, or reject to cancel.")
    return edited


def service_error(exc: BaseException) -> None:
    """A friendly message instead of a traceback."""
    st.error(
        "The service is unavailable right now "
        f"({type(exc).__name__}). "
        "Check the Gemini key in the .env file and try again."
    )
