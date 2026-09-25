"""Streamlit interface for the DJEF Personal Algerian Chef."""

from __future__ import annotations

import html
import sys
import uuid
from pathlib import Path
from typing import Any

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from notebook.chef_service import (  # noqa: E402
    ALGERIAN_MENU,
    ConfigurationError,
    conversation_config,
    get_graph,
    onboarding_message,
    service_status,
)

st.set_page_config(
    page_title="DJEF Chef · Personal Algerian Chef",
    page_icon="🇩🇿",
    layout="wide",
    initial_sidebar_state="expanded",
)

DIETARY_OPTIONS = (
    "No restrictions",
    "Vegetarian",
    "Vegan",
    "Halal",
    "Gluten-free",
    "Dairy-free",
)

WELCOME_MESSAGE = (
    "**Marhaba!** I'm **DJEF Chef**, your personal Algerian kitchen assistant. 🇩🇿\n\n"
    "Tell me what is waiting in your fridge, and I'll turn it into a specific Algerian "
    "dish — tlitli, harira, rechta, chakhchoukha, mhadjeb, and more."
)

EXAMPLE_PROMPTS = (
    "I have chickpeas, tomatoes, onion, and cumin. What can I make?",
    "I have semolina and tomatoes. Any Algerian ideas?",
    "Make today's recipe vegan for four people.",
    "What is the traditional way to cook chorba frik?",
)


# ---------------------------------------------------------------------------
# Visual design
# ---------------------------------------------------------------------------
def inject_styles() -> None:
    """Apply the Algerian green / warm spice visual system."""
    st.markdown(
        """
        <style>
        :root {
            --djef-green: #0b6b4f;
            --djef-green-dark: #064c39;
            --djef-mint: #dcefe6;
            --djef-cream: #fbf8f0;
            --djef-gold: #d49a32;
            --djef-ink: #17352a;
            --djef-muted: #66756e;
        }

        .stApp {
            background:
                radial-gradient(circle at 86% 4%, rgba(212, 154, 50, 0.10), transparent 24rem),
                radial-gradient(circle at 6% 90%, rgba(11, 107, 79, 0.08), transparent 28rem),
                var(--djef-cream);
            color: var(--djef-ink);
        }

        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stToolbar"] { right: 1rem; }
        .block-container { max-width: 1180px; padding-top: 1.4rem; padding-bottom: 4rem; }

        [data-testid="stSidebar"] {
            background: #073f31;
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }
        [data-testid="stSidebar"] * { color: #f5fbf8; }
        [data-testid="stSidebar"] .stCaption { color: #cfe6db !important; }
        [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.28);
            color: #f5fbf8 !important;
        }
        [data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
            background: rgba(255, 255, 255, 0.20);
            border-color: rgba(255, 255, 255, 0.45);
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] [data-baseweb="select"] * { color: #17352a; }

        .brand {
            display: flex;
            align-items: center;
            gap: .8rem;
            padding: .35rem 0 .9rem;
        }
        .brand-mark {
            width: 2.7rem;
            height: 2.7rem;
            display: grid;
            place-items: center;
            border-radius: .9rem;
            background: linear-gradient(145deg, #f4c96d, #c78321);
            box-shadow: 0 10px 25px rgba(0, 0, 0, .18);
            font-size: 1.35rem;
        }
        .brand-name {
            font-size: 1.15rem;
            font-weight: 800;
            letter-spacing: .12em;
        }
        .brand-kicker {
            color: #b8d4c8;
            font-size: .72rem;
            letter-spacing: .08em;
            text-transform: uppercase;
        }

        .hero {
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(11, 107, 79, .13);
            border-radius: 1.35rem;
            padding: 1.65rem 1.8rem;
            margin-bottom: 1rem;
            background: rgba(255, 255, 255, .72);
            box-shadow: 0 16px 48px rgba(22, 65, 49, .08);
            backdrop-filter: blur(12px);
        }
        .hero::after {
            content: "✦";
            position: absolute;
            right: 1.7rem;
            top: .8rem;
            color: rgba(212, 154, 50, .25);
            font-size: 4.2rem;
            line-height: 1;
        }
        .hero-eyebrow {
            color: var(--djef-green);
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .16em;
            text-transform: uppercase;
            margin-bottom: .3rem;
        }
        .hero h1 {
            color: var(--djef-ink);
            font-size: clamp(1.9rem, 4vw, 3rem);
            margin: 0;
            line-height: 1.08;
        }
        .hero p {
            color: var(--djef-muted);
            max-width: 700px;
            margin: .65rem 0 0;
            font-size: 1.02rem;
        }

        .profile-card, .setup-card {
            border: 1px solid rgba(11, 107, 79, .16);
            border-radius: 1.2rem;
            padding: 1.1rem;
            background: rgba(255, 255, 255, .78);
            box-shadow: 0 12px 34px rgba(22, 65, 49, .06);
            margin: 0 0 .8rem;
        }
        [data-testid="stSidebar"] .profile-card {
            background: rgba(255, 255, 255, 0.07);
            border-color: rgba(255, 255, 255, 0.14);
            box-shadow: none;
        }
        [data-testid="stSidebar"] .profile-name { color: #ffffff; }
        [data-testid="stSidebar"] .profile-label { color: #9fd0bd; }
        [data-testid="stSidebar"] .profile-value { color: #e6f4ee; }
        [data-testid="stSidebar"] .status-pill {
            border-color: rgba(255, 255, 255, 0.22);
            color: #f0faf5;
            background: rgba(255, 255, 255, 0.08);
        }
        .profile-name { color: white; font-size: 1.08rem; font-weight: 750; }
        .profile-label {
            color: #b8d4c8;
            font-size: .72rem;
            text-transform: uppercase;
            letter-spacing: .08em;
        }
        .profile-value { color: #f2faf6; font-size: .86rem; margin-top: .12rem; }
        .status-pill {
            display: inline-block;
            border: 1px solid rgba(255,255,255,.16);
            border-radius: 999px;
            padding: .25rem .62rem;
            margin: .15rem .15rem 0 0;
            color: #dcefe6;
            background: rgba(255,255,255,.07);
            font-size: .72rem;
        }

        .welcome-panel {
            max-width: 760px;
            margin: 2rem auto 0;
            padding: 2rem;
            border: 1px solid rgba(11, 107, 79, .13);
            border-radius: 1.5rem;
            background: rgba(255, 255, 255, .84);
            box-shadow: 0 22px 60px rgba(22, 65, 49, .10);
        }
        .welcome-icon { font-size: 2.8rem; }
        .welcome-panel h2 { margin: .3rem 0; color: var(--djef-ink); }
        .welcome-panel p { color: var(--djef-muted); }

        div[data-testid="stChatMessage"] {
            border: 1px solid rgba(11, 107, 79, .10);
            border-radius: 1.1rem;
            padding: .25rem .55rem;
            margin: .35rem 0 .8rem;
            background: rgba(255, 255, 255, .68);
            box-shadow: 0 8px 24px rgba(22, 65, 49, .05);
        }
        div[data-testid="stChatInput"] {
            border: 1px solid rgba(11, 107, 79, .20);
            border-radius: 1rem;
            background: rgba(255, 255, 255, .92);
            box-shadow: 0 14px 38px rgba(22, 65, 49, .10);
        }
        div[data-testid="stForm"] {
            border: 1px solid rgba(11, 107, 79, .13);
            border-radius: 1.2rem;
            padding: 1.25rem;
            background: rgba(255, 255, 255, .78);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------
def initialise_state() -> None:
    """Create state once, while preserving it during Streamlit reruns."""
    defaults = {
        "onboarding_complete": False,
        "name": "",
        "dietary_preferences": [],
        "allergies": "",
        "thread_id": uuid.uuid4().hex,
        "messages": [{"role": "assistant", "content": WELCOME_MESSAGE}],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_conversation() -> None:
    """Start a clean conversation with a new isolated LangGraph thread."""
    st.session_state.onboarding_complete = False
    st.session_state.name = ""
    st.session_state.dietary_preferences = []
    st.session_state.allergies = ""
    st.session_state.thread_id = uuid.uuid4().hex
    st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]
    st.rerun()


def message_text(message: Any) -> str:
    """Extract text from string and Gemini block-style message content."""
    text = getattr(message, "text", None)
    if isinstance(text, str) and text:
        return text

    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        pieces: list[str] = []
        for block in content:
            if isinstance(block, str):
                pieces.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                pieces.append(str(block.get("text", "")))
        return "".join(pieces)
    return ""


def response_from_state(graph: Any, config: dict[str, Any]) -> str:
    """Read the last AI message when a provider emitted no visible chunks."""
    snapshot = graph.get_state(config)
    messages = (snapshot.values or {}).get("messages", [])
    for message in reversed(messages):
        if message.__class__.__name__.startswith("AI"):
            return message_text(message)
    return ""


def run_chef_turn(prompt: str, thread_id: str) -> str:
    """Stream a chef answer and let the checkpointer save the full state."""
    graph = get_graph()
    config = conversation_config(thread_id)
    placeholder = st.empty()
    answer_parts: list[str] = []

    with st.status("DJEF Chef is checking your kitchen…", expanded=False) as status:
        for chunk, _metadata in graph.stream(
            {"messages": [{"role": "user", "content": prompt}]},
            config=config,
            stream_mode="messages",
        ):
            text = message_text(chunk)
            if text:
                answer_parts.append(text)
                placeholder.markdown("".join(answer_parts) + "▌")
                status.update(label="Writing your recipe…", state="running")

        answer = "".join(answer_parts).strip()
        if not answer:
            answer = response_from_state(graph, config).strip()

        if not answer:
            status.update(label="The chef could not prepare a reply", state="error")
            raise RuntimeError("The model returned an empty response.")

        status.update(label="Recipe ready", state="complete", expanded=False)

    placeholder.markdown(answer)
    return answer


def show_setup_status(status: dict[str, Any]) -> None:
    """Explain which optional/required integrations need attention."""
    if not status["gemini_configured"]:
        st.warning(
            "**Gemini setup required.** Copy `.env.example` to `.env`, add "
            "`GEMINI_API_KEY`, then restart Streamlit.",
            icon="🔑",
        )
    elif not status["tavily_configured"]:
        st.info(
            "Curated leftover matching is ready. Add `TAVILY_API_KEY` to enable "
            "live web recipe search.",
            icon="🌐",
        )


# ---------------------------------------------------------------------------
# Sidebar and screens
# ---------------------------------------------------------------------------
def render_sidebar(status: dict[str, Any]) -> None:
    """Render branding, profile memory, service status, and reset action."""
    with st.sidebar:
        st.markdown(
            """
            <div class="brand">
              <div class="brand-mark">👩‍🍳</div>
              <div>
                <div class="brand-name">DJEF</div>
                <div class="brand-kicker">Personal Algerian Chef</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.onboarding_complete:
            preferences = st.session_state.dietary_preferences or ["No restrictions"]
            safe_name = html.escape(st.session_state.name or "Cook")
            safe_preferences = ", ".join(html.escape(item) for item in preferences)
            safe_allergies = html.escape(st.session_state.allergies or "None shared")
            st.markdown(
                f"""
                <div class="profile-card">
                  <div class="profile-label">Remembered for this chat</div>
                  <div class="profile-name">👋 {safe_name}</div>
                  <div style="height:.55rem"></div>
                  <div class="profile-label">Kitchen style</div>
                  <div class="profile-value">{safe_preferences}</div>
                  <div class="profile-label" style="margin-top:.55rem">Avoid</div>
                  <div class="profile-value">{safe_allergies}</div>
                  <div style="height:.55rem"></div>
                  <span class="status-pill">🧠 Memory on</span>
                  <span class="status-pill">🔒 Isolated thread</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="profile-card">
                  <div class="profile-label">Your kitchen</div>
                  <div class="profile-name" style="margin-top:.25rem">
                    Set up in under a minute
                  </div>
                  <div class="profile-value">
                    Your name, diet, and allergies stay with this conversation.
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("#### Services")
        tavily_state = "connected" if status["tavily_configured"] else "optional / not set"
        tracing_state = "on" if status["tracing_enabled"] else "off"
        st.caption(
            f"🧠 Gemini · `{status['model']}`  \n"
            f"🌐 Tavily · {tavily_state}  \n"
            f"📈 LangSmith · tracing {tracing_state}"
        )
        st.markdown("---")
        if st.button("↻  Start a new conversation", use_container_width=True):
            reset_conversation()
        st.caption(
            "Memory uses LangGraph's in-RAM checkpointer and is cleared when the server stops."
        )
        st.markdown(
            "<div style='margin-top:1.2rem;color:#b8d4c8;font-size:.8rem'>"
            "Made with ❤ by <b>Kassouar Fatima</b></div>",
            unsafe_allow_html=True,
        )


def render_header(status: dict[str, Any]) -> None:
    """Render the compact product header and the Algerian-only menu."""
    st.markdown(
        """
        <div class="hero">
          <div class="hero-eyebrow">From leftovers to la darima</div>
          <h1>Cook what you already have.</h1>
          <p>A personal Algerian chef with a memory for your preferences, practical
             leftover recipes, and live recipe search when you need inspiration.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div style="color:#111111;font-weight:600;font-size:.92rem;margin:-.4rem 0 .9rem">
          🧠 Powered by <b>Gemini</b> · <code>{status['model']}</code>
          &nbsp;·&nbsp; 🌐 Tavily {"connected" if status["tavily_configured"] else "optional"}
          &nbsp;·&nbsp; 📈 LangSmith tracing {"on" if status["tracing_enabled"] else "off"}
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("🥘 DJEF's Algerian menu — only these dishes are recommended"):
        dish_rows = " · ".join(f"**{dish}**" for dish in ALGERIAN_MENU)
        st.markdown(
            f"<div style='line-height:1.9'>{dish_rows}</div>",
            unsafe_allow_html=True,
        )
        st.caption(
            "Ask for any of these with the ingredients you already have. If you want a "
            "dish outside this menu, DJEF will use web search and still keep it Algerian."
        )


def render_onboarding(status: dict[str, Any]) -> None:
    """Collect the profile once and store it in the first graph turn."""
    st.markdown(
        """
        <div class="welcome-panel">
          <div class="welcome-icon">🇩🇿</div>
          <h2>Let's set the table, <span style="color:#0b6b4f">chef</span>.</h2>
          <p>A few details help DJEF Chef keep every suggestion relevant and safe.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.15, 0.85], gap="large")
    with left, st.form("chef_profile", clear_on_submit=False):
        st.markdown("### 1 · Meet the chef")
        name = st.text_input(
            "What should I call you?",
            placeholder="e.g., Fatima",
            max_chars=60,
        )
        st.markdown("### 2 · Your table")
        preferences = st.multiselect(
            "Dietary preferences",
            DIETARY_OPTIONS,
            default=["No restrictions"],
            placeholder="Choose all that apply",
        )
        allergies = st.text_input(
            "Allergies or ingredients to avoid",
            placeholder="e.g., peanuts, shellfish",
            help=(
                "Please use blank if none. The chef will flag possible conflicts, "
                "not certify safety."
            ),
            max_chars=240,
        )
        submitted = st.form_submit_button(
            "Enter the kitchen  →",
            type="primary",
            use_container_width=True,
            disabled=not status["gemini_configured"],
        )

    with right:
        st.markdown(
            """
            <div class="setup-card" style="margin-top:1rem">
              <div style="font-size:2rem">🥣</div>
              <h3 style="margin:.35rem 0">What DJEF remembers</h3>
              <p style="color:#66756e">Your name, diet, and allergies are saved in the current
              LangGraph thread. They are available in later turns without asking again.</p>
              <p style="color:#66756e"><strong>Try:</strong> “I have chickpeas, tomatoes, onion,
              and cumin. What can I make?”</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if not submitted:
        return

    clean_preferences = [
        preference for preference in preferences if preference != "No restrictions"
    ]

    profile_prompt = onboarding_message(
        name=name,
        dietary_preferences=clean_preferences,
        allergies=allergies,
    )
    try:
        answer = run_chef_turn(profile_prompt, st.session_state.thread_id)
    except (ConfigurationError, RuntimeError) as exc:
        st.error(str(exc), icon="⚠️")
        return
    except Exception:
        st.error(
            "Gemini could not be reached. Check the key, model name, and internet "
            "connection, then try again.",
            icon="⚠️",
        )
        return

    st.session_state.name = name.strip()
    st.session_state.dietary_preferences = clean_preferences or ["No restrictions"]
    st.session_state.allergies = allergies.strip()
    st.session_state.onboarding_complete = True
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()


def render_chat(status: dict[str, Any]) -> None:
    """Display the conversation and handle a new user turn."""
    col_btn, _ = st.columns([0.30, 0.70])
    with col_btn:
        if st.button(
            "↻  Start a new conversation",
            use_container_width=True,
            type="secondary",
            key="reset_top",
        ):
            reset_conversation()

    for message in st.session_state.messages:
        with st.chat_message(
            message["role"],
            avatar="👩‍🍳" if message["role"] == "assistant" else "🧑‍🍳",
        ):
            st.markdown(message["content"])

    if len(st.session_state.messages) == 1:
        st.caption("Try one of these to get started:")
        for example in EXAMPLE_PROMPTS:
            st.caption(f"🍽️ {example}")

    prompt = st.chat_input(
        "Tell DJEF what is in your fridge…",
        disabled=not status["gemini_configured"],
    )
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍🍳"):
        st.markdown(prompt)

    try:
        answer = run_chef_turn(prompt, st.session_state.thread_id)
    except ConfigurationError as exc:
        st.error(str(exc), icon="🔑")
        return
    except Exception:
        st.error(
            "The chef could not finish that turn. Check your connection and API "
            "credits, then try again.",
            icon="⚠️",
        )
        return

    st.session_state.messages.append({"role": "assistant", "content": answer})


def main() -> None:
    """Run the Streamlit app."""
    initialise_state()
    status = service_status()
    inject_styles()
    render_sidebar(status)
    render_header(status)
    show_setup_status(status)

    if st.session_state.onboarding_complete:
        render_chat(status)
    else:
        render_onboarding(status)


if __name__ == "__main__":
    main()
