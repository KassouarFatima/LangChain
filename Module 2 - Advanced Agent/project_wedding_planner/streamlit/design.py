"""The look of the DJEF Travel & Event app (the blue & white theme lives in
.streamlit/config.toml — this file is the page, the header and the footer)."""
from __future__ import annotations

import streamlit as st


def page_config() -> None:
    """The page itself: title, icon, centered layout."""
    st.set_page_config(
        page_title="DJEF Wedding", page_icon="💍", layout="centered"
    )


def header() -> None:
    """What the visitor sees first."""
    st.title("💍 DJEF Wedding — Algerian wedding planner")
    st.caption(
        "Checklist · budget & allocation · traditions by wilaya · "
        "traiteur menu · live research"
    )
    st.caption(
        "One coordinator, three specialists — flights (MCP server) · "
        "venues (live web search) · playlist (SQL)"
    )
    st.caption("by Kassouar Fatima 🇩🇿")


def footer() -> None:
    """The honest note under every plan."""
    st.caption(
        "Indicative figures and portions (DA) — confirm them with your providers. "
        "Flight rows are demo data from the MCP server — confirm before booking."
    )


# ---------------------------------------------------------------------------
# Dark mode (toggled by the "🌙 Dark mode" button in the sidebar)
# ---------------------------------------------------------------------------
DARK_CSS = """
<style>
/* DJEF Travel & Event — dark mode overrides */
.stApp, [data-testid="stAppViewContainer"] { background: #0B1220 !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: #101B33 !important; }
h1, h2, h3, h4,
[data-testid="stMarkdownContainer"] p,
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] div {
    color: #E2E8F0 !important;
}
[data-testid="stCaptionContainer"] { color: #E2E8F0 !important; }
.wf-by { color: #E2E8F0 !important; }
.wf-name { color: #60A5FA !important; }
.stButton > button {
    background: #17233F !important; color: #E2E8F0 !important;
    border: 1px solid #33415C !important;
}
.stButton > button:hover { background: #1E2D52 !important; }
.stButton > button[kind="primary"] {
    background: #1D4ED8 !important; color: #FFFFFF !important;
    border-color: #1D4ED8 !important;
}
[data-baseweb="base-input"],
[data-testid="stTextInput"] input, [data-testid="stDateInput"] input {
    background: #17233F !important; color: #E2E8F0 !important;
    border-color: #33415C !important;
}
[data-baseweb="select"] { background: #17233F !important; }
[data-baseweb="select"] div, [data-baseweb="select"] input {
    color: #E2E8F0 !important;
}
div[data-baseweb="tag"] { background: #33415C !important; color: #E2E8F0 !important; }
[data-baseweb="menu"], ul[role="listbox"] { background: #17233F !important; }
ul[role="listbox"] li { color: #E2E8F0 !important; }
[data-testid="stAlert"] {
    background: #17233F !important; color: #E2E8F0 !important;
    border-color: #33415C !important;
}
hr { border-color: #33415C !important; }
[data-testid="stSpinner"], [data-testid="stSpinner"] p { color: #E2E8F0 !important; }
</style>
"""


def theme_css() -> None:
    """Dark-mode overrides — only when the sidebar switch says so."""
    if st.session_state.get("dark_mode"):
        st.markdown(DARK_CSS, unsafe_allow_html=True)
