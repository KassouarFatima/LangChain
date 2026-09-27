"""3.5 Email Agent — plain Python version.

by Kassouar Fatima 🇩🇿 — Module 3 — Production-Ready Agent.

Run:  python 3.5_email_agent.py
"""
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    dynamic_prompt,
    wrap_model_call,
)
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from langchain.messages import ToolMessage, HumanMessage

# ---------------------------------------------------------------------------
# Keys
# ---------------------------------------------------------------------------
load_dotenv()


def load_keys() -> str:
    """Return the Gemini API key from .env (never inside code)."""
    return os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY", "")


# ---------------------------------------------------------------------------
# Context + State
# ---------------------------------------------------------------------------
@dataclass
class EmailContext:
    """Credentials held in context (never state)."""

    email_address: str = "kassouarfatima@gmail.com"
    password: str = "password123"
    display_name: str = "Kassouar Fatima"


class AuthenticatedState(AgentState):
    """State extended with the authentication verdict."""

    authenticated: bool


# ---------------------------------------------------------------------------
# In-memory email store
# ---------------------------------------------------------------------------
_email_store: list[dict[str, Any]] = []


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _seed_emails() -> None:
    """Add initial emails if the store is empty."""
    if not _email_store:
        _email_store.extend([
            {
                "id": 1, "from": "fatima@example.com", "to": "kassouarfatima@gmail.com",
                "subject": "Coffee invitation",
                "body": "Hi! I'm going to be in town next week and was wondering if we could grab a coffee?\n- best, Fatima",
                "time": _now(), "type": "received",
            },
            {
                "id": 2, "from": "kassouarfatima@gmail.com", "to": "fatima@example.com",
                "subject": "Re: Coffee",
                "body": "I'll be there, bring the coffee!",
                "time": _now(), "type": "sent",
            },
            {
                "id": 3, "from": "boss@example.com", "to": "kassouarfatima@gmail.com",
                "subject": "Project deadline",
                "body": "Hi Kassouar, the project deadline is next Friday. Please confirm.\n- Boss",
                "time": _now(), "type": "received",
            },
        ])


_seed_emails()


# ---------------------------------------------------------------------------
# Simulated email helpers
# ---------------------------------------------------------------------------
def send_email_simulated(to: str, subject: str, body: str) -> str:
    """Store an email in memory and return a success message."""
    _email_store.append({
        "id": len(_email_store) + 1,
        "from": "kassouarfatima@gmail.com",
        "to": to,
        "subject": subject,
        "body": body,
        "time": _now(),
        "type": "sent",
    })
    return (
        f"✅ **Email sent!** 🇩🇿✉️\n\n"
        f"**Marhaba!** Your email has been sent successfully!\n"
        f"**To:** {to}\n"
        f"**Subject:** {subject}\n"
        f"**Body:** {body}\n"
        f"**Sent at:** {_now()}\n\n"
        f"🥳 **Mabrouk!** Message delivered! 🇩🇿\n"
        f"**Barak Allahu fik!** (God bless you) ✉️🌟"
    )


def receive_email_simulated() -> str:
    """Return all emails from the in-memory store."""
    if not _email_store:
        return "📭 **Your inbox is empty, Khoya!** 📭\n\nTry sending an email first! ✉️🇩🇿"
    lines = ["📬 **Your Inbox — Marhaba!** 🇩🇿📬\n"]
    for email in reversed(_email_store):
        lines.append(
            f"📥 [{email['time']}] {email['from']}\n"
            f"   **To:** {email['to']}\n"
            f"   **Subject:** {email['subject']}\n"
            f"   **Type:** {email['type']}\n"
            f"   {email['body'][:150]}{'…' if len(email['body']) > 150 else ''}\n"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
@tool
def check_inbox() -> str:
    """Check all emails in your inbox — received and sent, with timestamps."""
    return receive_email_simulated()


@tool
def receive_email() -> str:
    """Receive and read emails from your inbox."""
    return receive_email_simulated()


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to anyone (stored in memory)."""
    return send_email_simulated(to, subject, body)


@tool
def authenticate(email: str, password: str, runtime: ToolRuntime) -> Command:
    """Authenticate the user with the given email and password."""
    if email == runtime.context.email_address and password == runtime.context.password:
        return Command(
            update={
                "authenticated": True,
                "messages": [
                    ToolMessage(
                        "Marhaba! Successfully authenticated! Welcome to DJEF. ✉️🇩🇿",
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )
    return Command(
        update={
            "authenticated": False,
            "messages": [
                ToolMessage(
                    "Authentication failed. Check your email and password.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


# ---------------------------------------------------------------------------
# Dynamic middleware (ASYNC)
# ---------------------------------------------------------------------------
@wrap_model_call
async def dynamic_tool_call(request: Any, handler: Any) -> Any:
    """Allow full email tools after authentication."""
    authenticated = request.state.get("authenticated")
    if authenticated:
        request = request.override(
            tools=[authenticate, receive_email, check_inbox, send_email]
        )
    else:
        request = request.override(tools=[authenticate])
    return await handler(request)


authenticated_prompt = (
    "You are DJEF (Djazair Email Facilitator) — a full-featured Algerian email assistant. "
    "You have a warm, friendly Algerian personality. Use phrases like 'Marhaba!', 'Khoya!', 'Bienvenue!' naturally. "
    "You can: receive emails, check inbox, send emails. "
    "Always show timestamps for every email. Always show the sender and receiver. "
    "Your first step after authentication is to check the inbox. "
    "Be helpful, polite, and proudly Algerian. 🇩🇿"
)
unauthenticated_prompt = (
    "You are DJEF, a friendly Algerian email assistant. Greet users with 'Marhaba! ✉️🇩🇿' "
    "and ask them to authenticate with their email and password. "
    "Be warm, welcoming, and speak with Algerian charm."
)


@dynamic_prompt
def dynamic_prompt_fn(request: Any) -> str:
    """Generate system prompt based on authentication status."""
    return authenticated_prompt if request.state.get("authenticated") else unauthenticated_prompt


# ---------------------------------------------------------------------------
# Build the agent
# ---------------------------------------------------------------------------
def build_email_agent() -> Any:
    """Build the Email Agent with all middleware."""
    checkpointer = InMemorySaver()
    return create_agent(
        "google_genai:gemini-3.5-flash-lite",
        tools=[authenticate, receive_email, check_inbox, send_email],
        checkpointer=checkpointer,
        state_schema=AuthenticatedState,
        context_schema=EmailContext,
        middleware=[
            dynamic_tool_call,
            dynamic_prompt_fn,
            HumanInTheLoopMiddleware(
                interrupt_on={"authenticate": False, "receive_email": False, "check_inbox": False, "send_email": True}
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Run helpers (ASYNC)
# ---------------------------------------------------------------------------
async def run_email_agent(message: str, thread_id: str = "1", context: EmailContext | None = None) -> dict:
    """Send a message to the agent and return the raw response dict."""
    agent = build_email_agent()
    config = {"configurable": {"thread_id": thread_id}}
    response = await agent.ainvoke(
        {"messages": [HumanMessage(content=message.strip())]},
        context=context if context is not None else EmailContext(),
        config=config,
    )
    return response


async def resume_email_approval(thread_id: str = "1", decision: str = "approve", context: EmailContext | None = None) -> dict:
    """Resume the agent after an HITL interrupt."""
    agent = build_email_agent()
    config = {"configurable": {"thread_id": thread_id}}
    response = await agent.ainvoke(
        Command(resume={"decisions": [{"type": decision}]}),
        context=context if context is not None else EmailContext(),
        config=config,
    )
    return response


async def resume_email_edit(thread_id: str = "1", edited_body: str = "", context: EmailContext | None = None) -> dict:
    """Resume the agent after an HITL edit."""
    agent = build_email_agent()
    config = {"configurable": {"thread_id": thread_id}}
    response = await agent.ainvoke(
        Command(resume={"decisions": [{"type": "edit", "edited_action": {"name": "send_email", "args": {"body": edited_body}}}]}),
        context=context if context is not None else EmailContext(),
        config=config,
    )
    return response


def extract_interrupt_body(response: dict) -> str | None:
    """Extract the pending send_email body from an interrupted response."""
    try:
        interrupt = response["__interrupt__"][0]
        value = interrupt.value if hasattr(interrupt, "value") else interrupt["value"]
        return value["action_requests"][0]["args"]["body"]
    except (KeyError, IndexError, TypeError, AttributeError):
        return None


def last_text(response: dict) -> str:
    """Return the last human-readable text from the response."""
    msgs = response.get("messages", [])
    for msg in reversed(msgs):
        content = getattr(msg, "content", None)
        if content and isinstance(content, list):
            text = " ".join(str(c) for c in content if isinstance(c, str) and c)
            if text:
                return text
        elif content and isinstance(content, str):
            return content
    if msgs:
        last = msgs[-1]
        content = getattr(last, "content", str(last))
        if isinstance(content, list):
            content = " ".join(str(c) for c in content if isinstance(c, str))
        return str(content) if content else ""
    return ""


# ---------------------------------------------------------------------------
# Main — run the agent
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("🇩🇿 DJEF Email Assistant — by Kassouar Fatima")
    print("=" * 50)

    # Step 1: Authenticate
    print("\n🔐 Step 1: Authenticating...")
    response = asyncio.run(run_email_agent("kassouarfatima@gmail.com, password123"))
    print(f"Last text: {last_text(response)}")

    # Step 2: Check inbox
    print("\n📬 Step 2: Checking inbox...")
    response = asyncio.run(run_email_agent("check my inbox"))
    print(f"Last text: {last_text(response)}")

    # Step 3: Send email (will interrupt)
    print("\n✉️ Step 3: Sending email (will interrupt for approval)...")
    response = asyncio.run(run_email_agent("send an email to kassouarfatima20@gmail.com saying hello from Algeria"))
    interrupt_body = extract_interrupt_body(response)
    if interrupt_body:
        print(f"⏸️ HITL Interrupt! Draft body:\n{interrupt_body}")

        # Step 4: Approve
        print("\n✅ Step 4: Approving...")
        response = asyncio.run(resume_email_approval(decision="approve"))
        print(f"Last text: {last_text(response)}")
    else:
        print(f"Last text: {last_text(response)}")

    print("\nMabrouk! 🇩🇿 — by Kassouar Fatima")
