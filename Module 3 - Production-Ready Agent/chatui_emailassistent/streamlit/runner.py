"""Functionality of the DJEF Email Assistant app — agent invocation and HITL handling.

No widgets live here: keys, the agent build, the conversation context, and
the session's saved runs.

by Kassouar Fatima 🇩🇿 — Module 3 — Production-Ready Agent.
"""
from __future__ import annotations

import asyncio
from datetime import datetime

import streamlit as st

import email_agent_service as svc


# ---------------------------------------------------------------------------
# Keys + agent
# ---------------------------------------------------------------------------
def load_keys() -> str:
    """Load the Gemini key from the nearest .env — never inside code."""
    return svc.load_keys()


def get_agent():
    """Build the Email Agent once (module-level cache in email_agent_service)."""
    return svc.build_email_agent()


def mail_status() -> tuple[str, str]:
    """(kind, one-line summary) of the mail transport for the sidebar.

    kind is "real", "blocked" (MAIL_MODE=real but credentials missing) or
    "simulated" (built-in demo inbox — no mail server involved).
    """
    cfg = svc.mail_config()
    if cfg.usable:
        return "real", cfg.summary
    if cfg.forced_real:
        return "blocked", cfg.summary
    return "simulated", cfg.summary


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------
def build_context(auth: dict) -> svc.EmailContext:
    """Return the auth credentials as the EmailContext the agent receives."""
    return svc.EmailContext(
        email_address=auth.get("email", "kassouarfatima@gmail.com"),
        password=auth.get("password", "password123"),
        display_name="Kassouar Fatima",
    )


# ---------------------------------------------------------------------------
# Conversation helpers
# ---------------------------------------------------------------------------
def remember_run(title: str, text: str) -> None:
    """Keep the latest five runs of this session (newest first)."""
    st.session_state["runs"].insert(
        0,
        {
            "title": title.strip().splitlines()[0][:48],
            "at": datetime.now().strftime("%H:%M:%S"),
            "text": text,
        },
    )
    del st.session_state["runs"][6:]


# ---------------------------------------------------------------------------
# Run the agent
# ---------------------------------------------------------------------------
def run(message: str, auth: dict, thread_id: str) -> str:
    """Send a message to the agent and return the assistant's reply."""
    context = build_context(auth)
    st.session_state["context"] = context

    try:
        response = asyncio.run(
            svc.run_email_agent(message, thread_id=thread_id, context=context)
        )
    except Exception as e:
        return f"❌ **Error!** 🇩🇿\n\n**Saha,** something went wrong:\n```\n{type(e).__name__}: {e}\n```\n\nCheck the Gemini key in .env"

    interrupt_body = svc.extract_interrupt_body(response)
    if interrupt_body:
        st.session_state["interrupted"] = True
        st.session_state["thread_id"] = thread_id
        return f"__HITL__:{interrupt_body}"

    text = svc.last_text(response)
    remember_run(message, text)
    return text


def resume(decision: str, thread_id: str, edited_body: str = "") -> str:
    """Resume the agent after an HITL interrupt (approve / edit / reject)."""
    context = st.session_state.get("context", svc.EmailContext())
    with st.spinner(f"Processing {decision}…"):
        if decision == "edit":
            response = asyncio.run(
                svc.resume_email_edit(
                    thread_id=thread_id, edited_body=edited_body, context=context
                )
            )
        else:
            response = asyncio.run(
                svc.resume_email_approval(
                    thread_id=thread_id, decision=decision, context=context
                )
            )

    interrupt_body = svc.extract_interrupt_body(response)
    if interrupt_body:
        st.session_state["interrupted"] = True
        return f"__HITL__:{interrupt_body}"

    text = svc.last_text(response)
    remember_run(f"[{decision}] resume", text)
    st.session_state["interrupted"] = False
    return text


def get_all_emails_text() -> str:
    """Return a formatted string of all emails from the service."""
    return svc.list_all_emails()
