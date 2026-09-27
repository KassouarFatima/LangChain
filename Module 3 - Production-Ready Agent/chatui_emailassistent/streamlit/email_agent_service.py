"""Email Agent service — DJEF Email Assistant.

by Kassouar Fatima 🇩🇿 — Module 3 — Production-Ready Agent.

Full-featured Algerian email assistant:
  • check_inbox / receive_email — the inbox
  • send_email — deliver a message
  • send_file — image/PDF/video/voice attachments
  • authenticate — verify credentials
  • Human-in-the-Loop approval on send_email

MAIL MODE (the fix for `b'Empty username or password.'`)
---------------------------------------------------------
The tools never open a socket unless the credentials are actually usable.
  MAIL_MODE=auto       real Gmail when EMAIL_PASSWORD holds an App Password,
                       otherwise the built-in in-memory store (default, and
                       what README.md / 3.5_email_agent.py describe)
  MAIL_MODE=real       always attempt the network; failures are reported by
                       naming the exact .env key instead of leaking the raw
                       IMAP/SMTP reply
  MAIL_MODE=simulated  never touch the network

Settings are read from the nearest .env (walking up from this file) and are
re-read automatically whenever that file changes on disk — no restart needed.

Shared module — imported by streamlit/ via sys.path.
Keys load from .env (GOOGLE_API_KEY, SMTP/IMAP settings).
Model: google_genai:gemini-3.5-flash-lite.
"""
from __future__ import annotations

import os
import socket
import ssl
import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import dotenv_values, load_dotenv
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
# Settings — .env is the source of truth, empty means "not set"
# ---------------------------------------------------------------------------
_ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_ENV_PATH):
    load_dotenv(_ENV_PATH)

# Values that are never a real mailbox password.
_DEMO_PASSWORDS = {
    "", "password123", "changeme", "change-me", "change_me",
    "your_app_password", "your-app-password", "yourappassword",
    "your_password", "your-password", "xxx", "none", "null", "todo",
}

# (path, mtime, values) — invalidated automatically when .env is edited.
_ENV_CACHE: tuple[str, float, dict[str, str]] | None = None


def _find_env_file() -> str | None:
    """The nearest .env, starting at this file's folder and walking up."""
    directory = os.path.dirname(os.path.abspath(__file__))
    for _ in range(8):
        candidate = os.path.join(directory, ".env")
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(directory)
        if parent == directory:
            break
        directory = parent
    return None


def _env_values() -> dict[str, str]:
    """Parsed .env, re-read on disk change so edits apply without a restart."""
    global _ENV_CACHE
    path = _find_env_file()
    if path is None:
        return {}
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        return {}
    if _ENV_CACHE is None or _ENV_CACHE[0] != path or _ENV_CACHE[1] != mtime:
        try:
            parsed = dotenv_values(path) or {}
        except Exception:
            parsed = {}
        _ENV_CACHE = (path, mtime, {k: (v or "") for k, v in parsed.items()})
    return _ENV_CACHE[2]


def setting(name: str, default: str = "") -> str:
    """Read one setting from .env (preferred) or the process environment.

    Empty, whitespace-only and quoted-empty values are treated as UNSET.
    That is the whole fix for `b'Empty username or password.'`: the old
    `os.getenv("EMAIL_PASSWORD", "")` returned "" and logged in with a blank
    password, so Gmail answered with that exact message.
    """
    value = _env_values().get(name) or os.getenv(name) or ""
    value = str(value).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1].strip()
    return value if value else default


def load_keys() -> str:
    """Return the Gemini API key from .env (never inside code)."""
    return setting("GOOGLE_API_KEY") or setting("GEMINI_API_KEY")


# ---------------------------------------------------------------------------
# Context + State
# ---------------------------------------------------------------------------
@dataclass
class EmailContext:
    """Credentials held in context (never state)."""

    email_address: str = "kassouarfatima@gmail.com"
    password: str = "password123"
    display_name: str = "Kassouar Fatima"
    uploaded_file_path: str = ""
    uploaded_file_name: str = ""


class AuthenticatedState(AgentState):
    """State extended with the authentication verdict."""

    authenticated: bool


# ---------------------------------------------------------------------------
# In-memory email store (fallback when SMTP unavailable)
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
# Mail configuration — open a socket ONLY when credentials are usable
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class MailConfig:
    """Resolved transport settings plus the reason we are (not) using them."""

    mode: str            # "real" or "simulated"
    requested: str       # MAIL_MODE: auto | real | simulated
    address: str
    password: str
    smtp_host: str
    smtp_port: int
    imap_host: str
    imap_port: int
    reason: str          # "" when everything is actually in place

    @property
    def usable(self) -> bool:
        """True only when a real connection can legitimately be attempted.

        Re-validates the password here rather than trusting mail_config()'s
        `reason`: a blank or demo password can never open a socket, even if
        the resolution logic above is changed later.
        """
        if self.mode != "real" or self.reason:
            return False
        password = (self.password or "").strip()
        return bool(password) and password.lower() not in _DEMO_PASSWORDS

    @property
    def forced_real(self) -> bool:
        """MAIL_MODE=real was asked for but the credentials are missing."""
        return self.requested == "real" and bool(self.reason)

    @property
    def summary(self) -> str:
        """One line for the sidebar."""
        if self.usable:
            return f"Real mail · {self.address}"
        if self.forced_real:
            return f"Real mail requested · {self.reason}"
        return f"Demo inbox · {self.reason}"


def _derive_imap_host(smtp_host: str) -> str:
    """smtp.gmail.com -> imap.gmail.com; other providers usually share a host."""
    if smtp_host.startswith("smtp."):
        return "imap." + smtp_host[len("smtp."):]
    return smtp_host or "imap.gmail.com"


def _as_int(value: str, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def mail_config() -> MailConfig:
    """Resolve MAIL_MODE + credentials, always with an explicit reason.

    This function can never return "real" with a blank password — that
    combination is exactly what produced `b'Empty username or password.'`.
    """
    requested = setting("MAIL_MODE", "auto").lower()
    if requested not in ("auto", "real", "simulated"):
        requested = "auto"

    address = setting("EMAIL_ADDRESS", "kassouarfatima@gmail.com")
    password = setting("EMAIL_PASSWORD")
    smtp_host = setting("SMTP_HOST", "smtp.gmail.com")
    smtp_port = _as_int(setting("SMTP_PORT", "587"), 587)
    imap_host = setting("IMAP_HOST") or _derive_imap_host(smtp_host)
    imap_port = _as_int(setting("IMAP_PORT", "993"), 993)

    reason = ""
    if requested == "simulated":
        reason = "MAIL_MODE=simulated in .env"
    elif not password:
        reason = "EMAIL_PASSWORD is not set in .env"
    elif password.lower() in _DEMO_PASSWORDS:
        reason = (
            f"EMAIL_PASSWORD is the demo value '{password}' — "
            "Gmail needs a 16-character App Password"
        )

    mode = "simulated" if reason else "real"
    if requested == "real" and reason:
        mode = "real"       # asked for it: report it, do not hide it

    # address is defaulted by setting(), so it is never blank here.
    return MailConfig(
        mode=mode, requested=requested, address=address, password=password,
        smtp_host=smtp_host, smtp_port=smtp_port,
        imap_host=imap_host, imap_port=imap_port, reason=reason,
    )


def _config_error(protocol: str, cfg: MailConfig) -> str:
    """Actionable message naming the exact .env key — never a raw server reply."""
    return (
        f"❌ **{protocol} not configured** 🇩🇿\n\n"
        f"**Saha, Khoya** — {cfg.reason}.\n\n"
        f"Edit `.env` next to `app.py`:\n"
        f"```\n"
        f"EMAIL_ADDRESS={cfg.address or 'kassouarfatima@gmail.com'}\n"
        f"EMAIL_PASSWORD=<16-character Gmail App Password>\n"
        f"MAIL_MODE=real\n"
        f"```\n"
        f"**For Gmail:** turn on 2-Step Verification, then create an App Password at "
        f"https://myaccount.google.com/apppasswords\n\n"
        f"*Or leave `EMAIL_PASSWORD` empty and keep the built-in demo inbox — "
        f"the app runs with no mail server at all.* 🇩🇿"
    )


def _connection_error(protocol: str, cfg: MailConfig, exc: BaseException) -> str:
    """Map a library exception to something a human can act on."""
    text = str(exc)
    if protocol == "IMAP":
        host, port = cfg.imap_host, cfg.imap_port
    else:
        host, port = cfg.smtp_host, cfg.smtp_port

    if "Empty username or password" in text or "LOGIN failed" in text:
        hint = (
            f"`{host}` rejected **{cfg.address}** because the password sent was blank. "
            f"Set `EMAIL_PASSWORD` in `.env` to a real App Password."
        )
    elif isinstance(exc, smtplib.SMTPAuthenticationError) or "AUTH" in text.upper() or "Invalid credentials" in text:
        hint = (
            f"`{host}` refused the login for **{cfg.address}**. Gmail needs an "
            f"**App Password** (https://myaccount.google.com/apppasswords), "
            f"not your normal account password."
        )
    elif isinstance(exc, socket.gaierror) or "getaddrinfo" in text or "Name or service not known" in text:
        hint = f"Cannot resolve `{host}` — check `IMAP_HOST` / `SMTP_HOST` in `.env`."
    elif isinstance(exc, ssl.SSLError):
        hint = f"TLS handshake with `{host}:{port}` failed — check the port setting."
    elif isinstance(exc, (TimeoutError, socket.timeout)) or "timed out" in text.lower():
        hint = f"`{host}:{port}` timed out — check your connection or firewall."
    elif isinstance(exc, ConnectionRefusedError) or getattr(exc, "errno", None) == 10061:
        hint = f"`{host}:{port}` refused the connection — check the host and port."
    else:
        hint = f"`{type(exc).__name__}: {text}`"

    return (
        f"❌ **{protocol} error** 🇩🇿\n\n"
        f"**Saha,** {hint}\n\n"
        f"**Mode:** `{cfg.requested}` → `{cfg.mode}` · "
        f"**Host:** `{host}:{port}` · **User:** `{cfg.address}`\n\n"
        f"Settings live in `.env` next to `app.py`: `EMAIL_ADDRESS`, "
        f"`EMAIL_PASSWORD`, `SMTP_HOST`, `SMTP_PORT`, `IMAP_HOST`, `IMAP_PORT`, "
        f"`MAIL_MODE`.\n\n"
        f"*Prefer to skip the mail server entirely?* Set `MAIL_MODE=simulated` "
        f"and the built-in demo inbox is used instead. 🇩🇿"
    )


# ---------------------------------------------------------------------------
# SMTP / IMAP helpers — real email sending and receiving (real mode only)
# ---------------------------------------------------------------------------
def send_email_smtp(to: str, subject: str, body: str, attachments: list[str] = None,
                    cfg: MailConfig | None = None) -> str:
    """Send a real email via SMTP. Refuses to connect without usable credentials."""
    cfg = cfg or mail_config()
    if not cfg.usable:
        return _config_error("SMTP", cfg)

    from_addr, from_pw = cfg.address, cfg.password
    try:
        msg = MIMEMultipart()
        msg["From"] = from_addr
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        for fpath in attachments or []:
            if fpath and Path(fpath).exists():
                with open(fpath, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f'attachment; filename="{Path(fpath).name}"')
                msg.attach(part)

        with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port, timeout=30) as server:
            server.starttls()
            server.login(from_addr, from_pw)
            server.sendmail(from_addr, to, msg.as_string())

        return (
            f"✅ **Email sent!** 🇩🇿✉️\n\n"
            f"**Marhaba!** Your email has been sent successfully!\n"
            f"**To:** {to}\n"
            f"**Subject:** {subject}\n"
            f"**Body:** {body}\n"
            f"**Sent at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"**From:** {from_addr}\n\n"
            f"🥳 **Mabrouk!** Message delivered! 🇩🇿\n"
            f"**Barak Allahu fik!** (God bless you) ✉️🌟"
        )
    except Exception as exc:
        return _connection_error("SMTP", cfg, exc)


def receive_email_imap(cfg: MailConfig | None = None) -> str:
    """Fetch emails from the inbox via IMAP. Refuses to connect on blank credentials."""
    cfg = cfg or mail_config()
    if not cfg.usable:
        return _config_error("IMAP", cfg)

    mail: imaplib.IMAP4_SSL | None = None
    try:
        mail = imaplib.IMAP4_SSL(cfg.imap_host, cfg.imap_port, timeout=30)
        mail.login(cfg.address, cfg.password)
        mail.select("INBOX")
        result, data = mail.search(None, "ALL")
        email_ids = (data[0] if result == "OK" and data else b"").split()[-10:]

        lines = ["📬 **Your Real Inbox — Marhaba!** 🇩🇿📬\n"]
        for eid in reversed(email_ids):
            _, msg_data = mail.fetch(eid, "(RFC822)")
            raw_msg = msg_data[0][1]
            msg = email.message_from_bytes(raw_msg)
            subject = msg["Subject"] or "(no subject)"
            sender = msg["From"] or "(unknown)"
            date = msg["Date"] or "(unknown)"
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        body = (payload or b"").decode("utf-8", errors="ignore")
                        break
            else:
                payload = msg.get_payload(decode=True)
                body = (payload or b"").decode("utf-8", errors="ignore")
            lines.append(
                f"📥 [{date}] {sender}\n   **Subject:** {subject}\n"
                f"   {body[:100]}{'…' if len(body) > 100 else ''}\n"
            )

        if len(lines) == 1:
            return "📭 **Your inbox is empty, Khoya!** 📭\n\nTry sending an email first! ✉️🇩🇿"
        return "\n".join(lines)
    except Exception as exc:
        return _connection_error("IMAP", cfg, exc)
    finally:
        if mail is not None:
            try:
                mail.logout()
            except Exception:
                pass


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
        f"**Sent at:** {_now()}\n"
        f"**From:** kassouarfatima@gmail.com\n\n"
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


def list_all_emails() -> str:
    """Return a formatted list of all sent and received emails."""
    if not _email_store:
        return "📭 **No emails yet, Khoya!** 📭"
    sent = [e for e in _email_store if e["type"] == "sent"]
    received = [e for e in _email_store if e["type"] == "received"]
    lines = [
        "### 📬 **All Emails — Sent & Received** 📬\n",
        f"**📤 Sent ({len(sent)}):**",
    ]
    for e in sent:
        lines.append(
            f"  · [{e['time']}] → **{e['to']}** — _{e['subject']}_\n"
            f"    {e['body'][:80]}{'…' if len(e['body']) > 80 else ''}"
        )
    lines.append(f"\n**📥 Received ({len(received)}):**")
    for e in received:
        lines.append(
            f"  · [{e['time']}] ← **{e['from']}** — _{e['subject']}_\n"
            f"    {e['body'][:80]}{'…' if len(e['body']) > 80 else ''}"
        )
    lines.append(f"\n**Total: {len(_email_store)} emails** 🇩🇿")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Transport dispatch — real when configured, built-in store otherwise
# ---------------------------------------------------------------------------
def fetch_inbox() -> str:
    """Inbox text: real IMAP when usable, the in-memory store otherwise."""
    cfg = mail_config()
    if cfg.usable:
        return receive_email_imap(cfg)
    if cfg.forced_real:
        return _config_error("IMAP", cfg)
    return receive_email_simulated()


def deliver_email(to: str, subject: str, body: str, attachments: list[str] | None = None) -> str:
    """Send text: real SMTP when usable, the in-memory store otherwise."""
    cfg = mail_config()
    if cfg.usable:
        return send_email_smtp(to, subject, body, attachments, cfg)
    if cfg.forced_real:
        return _config_error("SMTP", cfg)

    text = send_email_simulated(to, subject, body)
    real = [a for a in (attachments or []) if a and Path(a).exists()]
    if real:
        text += (
            f"\n\n📎 **Attachments kept locally (demo inbox):** "
            f"{', '.join(Path(a).name for a in real)}\n"
            f"*Set `EMAIL_PASSWORD` in `.env` to send them for real.* 🇩🇿"
        )
    return text


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
@tool
def check_inbox() -> str:
    """Check all emails in your inbox — received and sent, with timestamps."""
    return fetch_inbox()


@tool
def receive_email() -> str:
    """Receive and read emails from your inbox."""
    return fetch_inbox()


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to any address."""
    return deliver_email(to, subject, body)


@tool
def send_file(to: str, subject: str, body: str, file_path: str, file_type: str, runtime: ToolRuntime) -> str:
    """Send a file (image, PDF, video, voice) as an email attachment via SMTP."""
    valid_types = ["image", "pdf", "video", "voice"]
    if file_type.lower() not in valid_types:
        return f"❌ Invalid file type: '{file_type}'. Must be one of: {', '.join(valid_types)}. **Saha,** check your file type!"
    # Use uploaded file path from context if available
    fpath = file_path
    if not fpath or not fpath.strip():
        fpath = getattr(runtime.context, "uploaded_file_path", "") or ""
    attachments = [fpath] if fpath else []
    full_subject = f"[{file_type.upper()}] {subject}"
    return deliver_email(to, full_subject, body, attachments)


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
            tools=[authenticate, receive_email, check_inbox, send_email, send_file]
        )
    else:
        request = request.override(tools=[authenticate])
    return await handler(request)


authenticated_prompt = (
    "You are DJEF (Djazair Email Facilitator) — a full-featured Algerian email assistant. "
    "You have a warm, friendly Algerian personality. Use phrases like 'Marhaba!', 'Khoya!', 'Bienvenue!' naturally. "
    "You can: receive emails, check inbox, send emails, and send files "
    "(image, PDF, video, voice) as attachments. "
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
# Build the agent (module-level cache)
# ---------------------------------------------------------------------------
_agent_cache: dict[str, Any] = {}


def clear_cache() -> None:
    """Clear the agent cache so the next call builds a fresh agent."""
    _agent_cache.clear()


def build_email_agent() -> Any:
    """Build the Email Agent once (cached by thread_id)."""
    thread_id = "1"
    if thread_id not in _agent_cache:
        checkpointer = InMemorySaver()
        _agent_cache[thread_id] = create_agent(
            "google_genai:gemini-3.5-flash-lite",
            tools=[authenticate, receive_email, check_inbox, send_email, send_file],
            checkpointer=checkpointer,
            state_schema=AuthenticatedState,
            context_schema=EmailContext,
            middleware=[
                dynamic_tool_call,
                dynamic_prompt_fn,
                HumanInTheLoopMiddleware(
                    interrupt_on={"authenticate": False, "receive_email": False, "check_inbox": False, "send_email": True, "send_file": True}
                ),
            ],
        )
    return _agent_cache[thread_id]


# ---------------------------------------------------------------------------
# Run helpers (ASYNC)
# ---------------------------------------------------------------------------
async def run_email_agent(
    message: str, thread_id: str = "1", context: EmailContext | None = None
) -> dict:
    """Send a message to the agent and return the raw response dict."""
    agent = build_email_agent()
    config = {"configurable": {"thread_id": thread_id}}
    response = await agent.ainvoke(
        {"messages": [HumanMessage(content=message.strip())]},
        context=context if context is not None else EmailContext(),
        config=config,
    )
    return response


async def resume_email_approval(
    thread_id: str = "1", decision: str = "approve", context: EmailContext | None = None
) -> dict:
    """Resume the agent after an HITL interrupt with approve/reject."""
    agent = build_email_agent()
    config = {"configurable": {"thread_id": thread_id}}
    response = await agent.ainvoke(
        Command(resume={"decisions": [{"type": decision}]}),
        context=context if context is not None else EmailContext(),
        config=config,
    )
    return response


async def resume_email_edit(
    thread_id: str = "1", edited_body: str = "", context: EmailContext | None = None
) -> dict:
    """Resume the agent after an HITL edit with a user-modified draft."""
    agent = build_email_agent()
    config = {"configurable": {"thread_id": thread_id}}
    args: dict[str, Any] = {}
    name = "send_email"
    try:
        snapshot = await agent.aget_state(config)
        task = snapshot.tasks[0]
        value = task.interrupts[0].value
        action = value["action_requests"][0]
        name = action.get("name", name)
        args = dict(action.get("args") or {})
    except (AttributeError, IndexError, KeyError, TypeError):
        args = {}
    args["body"] = edited_body
    response = await agent.ainvoke(
        Command(resume={"decisions": [{"type": "edit", "edited_action": {"name": name, "args": args}}]}),
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
