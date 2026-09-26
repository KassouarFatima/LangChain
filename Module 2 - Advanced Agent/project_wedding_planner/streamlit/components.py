"""The widgets of the DJEF Wedding app — one small function per widget or button."""
from __future__ import annotations

import streamlit as st

import runner

WILAYAS = ["Alger", "Tlemcen", "Kabylie", "Constantine", "Oran", "Ouargla"]
STYLES = ["simple", "classic", "luxury"]
PRIORITIES = [
    "Venue (salon des fêtes)",
    "Traiteur & menu",
    "Budget",
    "Photo & video",
    "Decoration",
    "Dress & tenue",
    "Music & zaffa",
    "Traditions & rituals",
]
GENRES = ["Chaabi", "Rai", "Andalous", "Kabyle", "Melhoun", "Pop", "Rap", "Electro"]
SAMPLE_BRIEF = (
    "We are 100 guests for a wedding in Tlemcen on 20 June 2027, classic style, "
    "and our budget limit is 800 000 DA. Our priorities: the traiteur and the "
    "photo/video. We fly in from Paris and want a chaabi playlist. Give me the "
    "full plan: timeline, budget in DA, local traditions and the menu — plus the "
    "flights from Paris, a venue in Tlemcen for 100 guests and the playlist."
)


# --- sidebar ---------------------------------------------------------------
def sidebar_top() -> None:
    """The signature and the light/dark switch — the first things in the sidebar."""
    with st.sidebar:
        st.markdown(
            '<p style="font-size:.9rem;margin:0 0 .2rem">'
            '<span class="wf-by" style="color:#000000">by</span> '
            '<span class="wf-name" style="color:#1D4ED8;font-weight:700">Kassouar</span> '
            '<span class="wf-by" style="color:#000000">Fatima</span></p>',
            unsafe_allow_html=True,
        )
        theme_button()


def theme_button() -> None:
    """Switch the app between light and dark."""
    dark = bool(st.session_state.get("dark_mode", False))
    if st.button("☀️ Light mode" if dark else "🌙 Dark mode", key="theme_toggle"):
        st.session_state["dark_mode"] = not dark
        st.rerun()


def sidebar_wedding() -> dict:
    """The wedding facts: every input of the sidebar.

    The old fields stay untouched; the two new coordinator parameters —
    Origin and Playlist genre — are added underneath (Wilaya doubles as the
    coordinator's `Destination`).
    """
    with st.sidebar:
        st.header("The wedding")
        guests = st.number_input(
            "Number of guests", min_value=20, max_value=1000, value=100, step=10
        )
        wilaya = st.selectbox("Wilaya", WILAYAS)
        style = st.selectbox("Style", STYLES)
        wedding_date = st.date_input("Wedding date")
        budget_limit = st.number_input(
            "Budget limit (DA)",
            min_value=0,
            max_value=runner.wp.BUDGET_MAX,
            step=runner.wp.BUDGET_STEP,
            value=0,
            help="Your ceiling — 0 = no limit. A real budget sits between "
            "100 000 and 3 000 000 DA (step 50 000). Values like 50, 100 or "
            "500 DA are rejected with a warning and never sent to the model.",
        )
        _da = lambda n: f"{n:,}".replace(",", " ")
        if budget_limit == 0:
            st.info(
                "0 = no limit — the model plans without a ceiling. "
                f"A real budget sits between {_da(runner.wp.BUDGET_MIN_VALID)} "
                f"and {_da(runner.wp.BUDGET_MAX)} DA."
            )
        elif not runner.wp.valid_budget(budget_limit):
            st.warning(
                f"{_da(budget_limit)} DA is outside the valid range "
                f"(0 = no limit, or {_da(runner.wp.BUDGET_MIN_VALID)} – "
                f"{_da(runner.wp.BUDGET_MAX)} DA). This value will not be "
                "sent to the model — enter your real ceiling."
            )
        priorities = st.multiselect(
            "Priorities", PRIORITIES, default=["Traiteur & menu", "Photo & video"]
        )
        st.divider()
        origin = st.text_input(
            "Origin (where guests fly from)",
            value="Paris",
            help="Coordinator parameter 1 — the Flights Agent (MCP server) "
            "only ever receives this.",
        )
        genre = st.selectbox(
            "Playlist genre",
            GENRES,
            help="Coordinator parameter 4 — the Playlist Agent (SQL query) "
            "only ever receives this. Destination = Wilaya, Guest_Count = "
            "Number of guests.",
        )
    return {
        "guests": guests,
        "wilaya": wilaya,
        "style": style,
        "date": wedding_date,
        "budget_limit": budget_limit,
        "priorities": priorities,
        "origin": origin.strip() or "Paris",
        "genre": genre,
    }


def sample_brief_button() -> None:
    """Button: fill the request box with the showcase brief."""
    with st.sidebar:
        if st.button("Load sample brief", use_container_width=True):
            st.session_state["question_box"] = SAMPLE_BRIEF


def saved_runs_sidebar() -> str:
    """Sidebar list of this session's plans; returns the reopened title."""
    with st.sidebar:
        st.divider()
        st.markdown("**Saved runs**")
        titles = runner.saved_titles()
        if titles:
            return st.selectbox("Reopen", ["(none)"] + titles)
        st.caption("No runs yet.")
    return "(none)"


# --- main column -----------------------------------------------------------
def request_box() -> str:
    """The request box (filled by the sample brief button)."""
    return st.text_area(
        "Your request",
        key="question_box",
        placeholder="e.g. give me the full plan — timeline, budget, traditions, "
        "menu · or: flights from Paris, venue in Tlemcen for 100 guests, "
        "chaabi playlist",
        height=120,
    )


def prepare_button() -> bool:
    """The one blue button."""
    return st.button(
        "Prepare the plan 💍", type="primary", use_container_width=True
    )


def empty_request_note() -> None:
    st.info("Write your request first.")


def show_plan(text: str | None) -> None:
    """The plan itself + the .md download (only when there is a plan)."""
    if not text:
        return
    st.markdown(text)
    st.download_button(
        "Download this plan (.md)",
        data=text,
        file_name=runner.make_slug(text) + ".md",
        mime="text/markdown",
        use_container_width=True,
    )


def service_error(exc: BaseException) -> None:
    """A friendly message instead of a traceback."""
    st.error(
        "The service is unavailable right now "
        f"({type(exc).__name__}). "
        "Check the Gemini key in the .env file and try again."
    )
