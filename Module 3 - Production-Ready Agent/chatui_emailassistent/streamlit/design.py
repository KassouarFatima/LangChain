"""Visual design — DJEF Email Assistant.

Professional Algerian green / gold visual system.
Dark mode only, hero banner, chat styling, sidebar theme.

by Kassouar Fatima 🇩🇿 — Module 3 — Production-Ready Agent.
"""
from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# Algerian color system
# ---------------------------------------------------------------------------
GREEN       = "#0b6b4f"   # Algerian green
GREEN_DARK  = "#064c39"   # dark green
GOLD        = "#d49a32"   # warm gold
CREAM       = "#fbf8f0"   # cream background
MINT        = "#dcefe6"   # very light mint
INK         = "#17352a"   # dark ink
MUTED       = "#66756e"   # muted text
SIDEBAR_BG  = "#073f31"   # dark-green sidebar


def page_config() -> None:
    """Page metadata — first streamlit command on the page."""
    st.set_page_config(
        page_title="DJEF Email Assistant",
        page_icon="🇩🇿",
        layout="centered",
        initial_sidebar_state="expanded",
    )


# ---------------------------------------------------------------------------
# Hero banner — the professional first impression
# ---------------------------------------------------------------------------
def hero_banner() -> None:
    """Large branded hero section at the top of the app."""
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #0b6b4f 0%, #073f31 50%, #064c39 100%);
            border-radius: 16px;
            padding: 2.5rem 2rem;
            margin-bottom: 1.5rem;
            text-align: center;
            border: 1px solid rgba(212, 154, 50, 0.3);
            box-shadow: 0 4px 24px rgba(11, 107, 79, 0.25);
        ">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">🇩🇿✉️</div>
            <h1 style="
                color: #fbf8f0;
                font-size: 2.2rem;
                margin: 0 0 0.3rem;
                font-weight: 800;
                letter-spacing: -0.5px;
            ">DJEF Email Assistant</h1>
            <p style="
                color: #d49a32;
                font-size: 1.1rem;
                margin: 0 0 0.8rem;
                font-weight: 500;
            ">Marhaba! Your Algerian email assistant</p>
            <p style="
                color: rgba(245, 251, 248, 0.75);
                font-size: 0.9rem;
                margin: 0;
                line-height: 1.5;
            ">
                Authenticate · Check Inbox · Send Email
                <span style="color: #d49a32; font-weight: 700;">· Human-in-the-Loop</span>
            </p>
            <p style="
                color: rgba(212, 154, 50, 0.6);
                font-size: 0.75rem;
                margin: 0.5rem 0 0;
            ">
                🇩🇿 By Kassouar Fatima — Module 3 — Production-Ready Agent
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Sub-header with author
# ---------------------------------------------------------------------------
def sub_header() -> None:
    """Author line below the hero."""
    st.caption("**by Kassouar Fatima 🇩🇿**  ·  Module 3 — Production-Ready Agent")


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
def footer() -> None:
    """Professional footer under the chat."""
    st.markdown(
        """
        <div style="
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(11, 107, 79, 0.15);
            text-align: center;
        ">
            <p style="color: #66756e; font-size: 0.8rem; margin: 0;">
                ✉️ DJEF Email Assistant · powered by LangChain
                · <strong>Human-in-the-Loop</strong> on send_email
            </p>
            <p style="color: #0b6b4f; font-size: 0.75rem; margin: 0.3rem 0 0;">
                by Kassouar Fatima 🇩🇿
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Algerian theme CSS — dark only
# ---------------------------------------------------------------------------
DARK_CSS = """
<style>
/* ===== Dark Mode — Algerian green / gold on dark ===== */
:root { --djef-green: #0b6b4f; --djef-gold: #d49a32; --djef-ink: #e2e8f0; }

.stApp, [data-testid="stAppViewContainer"] {
    background: #0b1120 !important; color: #e2e8f0 !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { right: 1rem; }
[data-testid="stDecoration"] { display: none; }
.block-container { max-width: 1180px; padding-top: 1rem; padding-bottom: 3rem; }

/* Sidebar — deep Algerian green */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #063025 0%, #0a2e1f 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] * { color: #f5fbf8 !important; }
[data-testid="stSidebar"] .stCaption { color: #cfe6db !important; font-size: 0.85rem; }
[data-testid="stSidebar"] code { color: #0B6B4F !important; }
[data-testid="stSidebar"] .stDivider { border-color: rgba(255,255,255,0.10) !important; }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(11,107,79,0.20) !important;
    border: 1px solid rgba(11,107,79,0.40) !important;
    color: #f5fbf8 !important; border-radius: 8px;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(11,107,79,0.40) !important;
    border-color: rgba(11,107,79,0.60) !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #0b6b4f !important; color: #fff !important;
    border-color: #0b6b4f !important; border-radius: 8px;
}

/* Inputs */
[data-baseweb="base-input"], [data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea, [data-baseweb="select"] {
    background: #131d30 !important; color: #e2e8f0 !important;
    border: 1px solid #1e2d45 !important; border-radius: 8px;
}
div[data-baseweb="tag"] { background: #1e2d45 !important; color: #e2e8f0 !important; }
ul[role="listbox"] { background: #131d30 !important; }
[data-testid="stAlert"] { background: #131d30 !important; border: 1px solid #1e2d45 !important; border-radius: 10px; }
hr { border-color: #1e2d45 !important; }
[data-testid="stSpinner"] p { color: #0b6b4f !important; }

/* Primary button */
.stButton > button[kind="primary"] {
    background: #0b6b4f !important; color: #fff !important;
    border-color: #0b6b4f !important; border-radius: 8px;
    font-weight: 600;
}
.stButton > button[kind="primary"]:hover { background: #064c39 !important; }
.stButton > button[kind="secondary"] {
    background: rgba(11,107,79,0.15) !important; color: #e2e8f0 !important;
    border: 1px solid rgba(11,107,79,0.30) !important; border-radius: 8px;
}

/* Chat messages */
.stChatMessage {
    background: rgba(11,107,79,0.08) !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    border-left: 3px solid #0b6b4f !important;
    margin-bottom: 0.5rem;
    color: #e2e8f0 !important;
}
.stChatMessage p, .stChatMessage div, .stChatMessage span, .stChatMessage strong, .stChatMessage em, .stChatMessage b, .stChatMessage i, .stChatMessage li, .stChatMessage a { color: #e2e8f0 !important; }
.stMarkdown p, .stMarkdown div, .stMarkdown span, .stMarkdown a { color: #e2e8f0 !important; }
.stChatMessage * { color: #e2e8f0 !important; }
.stChatMessage[data-testid="stChatMessage"][role="log"] {
    background: rgba(11,107,79,0.05) !important;
}

/* Ensure all text is visible */
.stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown span,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
.stMarkdown h5, .stMarkdown h6, .stMarkdown li, .stMarkdown a,
.stMarkdown strong, .stMarkdown em, .stMarkdown b, .stMarkdown i {
    color: #e2e8f0 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #0b1120; }
::-webkit-scrollbar-thumb { background: #0b6b4f; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #064c39; }
</style>
"""

def theme_css() -> None:
    """Apply dark mode CSS only.

    This must render on *every* run through a plain ``st.markdown`` call.

    It previously cached an ``st.empty()`` placeholder in a module-level global.
    Streamlit caches imported modules in ``sys.modules``, so that global survived
    reruns and new sessions and kept pointing at a delta path recorded during an
    earlier run. Once the path went stale the update was dropped silently: the
    ``<style>`` never reached the DOM, ``.stApp`` lost its dark ``#0b1120``
    background, and the light ``#e2e8f0`` body text was left sitting on a white
    page -- invisible text.
    """
    st.markdown(DARK_CSS, unsafe_allow_html=True)


def toggle_mode() -> None:
    """Dark mode only — no toggle needed."""
    pass
