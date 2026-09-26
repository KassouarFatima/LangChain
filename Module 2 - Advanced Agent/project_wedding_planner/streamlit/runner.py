"""Functionality of the DJEF Travel & Event app — the part that talks to the service.

No widgets live here: keys, the team (coordinator + three specialists), the
context the coordinator receives, and the session's saved runs.
"""
from __future__ import annotations

import pathlib
import sys
from datetime import datetime

_SERVICE_FOLDER = pathlib.Path(__file__).resolve().parent.parent / "notebooks"
if str(_SERVICE_FOLDER) not in sys.path:
    sys.path.insert(0, str(_SERVICE_FOLDER))

import streamlit as st
from langchain.messages import HumanMessage

import wedding_planner_service as wp


def load_keys() -> str:
    """Load the Gemini/Tavily keys from the nearest .env — never inside code."""
    return wp.load_keys()


@st.cache_resource
def get_agent():
    """Build the team once (coordinator + specialists, cached across reruns)."""
    return wp.build_event_agent()


def build_context(question: str, wedding: dict) -> str:
    """The request plus the sidebar facts, as the coordinator sees them.

    The four dispatch parameters are named exactly as the spec wants them
    (Origin from the sidebar's Origin, Destination from the Wilaya); the
    remaining wedding facts ride along as extra context.
    """
    lines = [
        question.strip(),
        f"[Context] Origin={wedding['origin']}, Destination={wedding['wilaya']}, "
        f"Guest_Count={wedding['guests']}, Genre={wedding['genre']}, "
        f"style={wedding['style']}, date={wedding['date']:%d-%m-%Y}",
    ]
    budget = wedding.get("budget_limit") or 0
    if budget == 0:
        pass  # 0 = no limit: the old behaviour — no budget line at all
    elif wp.valid_budget(budget):
        lines.append(f"budget_limit={budget} DA")
    else:
        # Out of the range (50, 100, 500 …): tell the model instead of
        # feeding it an impossible ceiling — it must ask, not guess.
        lines.append(
            f"budget_limit=OUT OF RANGE ({budget} DA entered; valid = 0 = no "
            f"limit, or {wp.BUDGET_MIN_VALID}-{wp.BUDGET_MAX} DA) — ask the "
            "user for a real figure"
        )
    if wedding.get("priorities"):
        lines.append("priorities: " + ", ".join(wedding["priorities"]))
    return "\n".join(lines)


def run_plan(question: str, wedding: dict) -> str:
    """Ask the team for a plan and remember it among the saved runs."""
    context = build_context(question, wedding)
    with st.spinner("DJEF Wedding is preparing your plan…"):
        response = get_agent().invoke(
            {"messages": [HumanMessage(content=context)]}
        )
        answer = wp.last_text(response)
    remember_plan(question, answer)
    return answer


# --- saved runs (session history) ------------------------------------------
def remember_plan(question: str, answer: str) -> None:
    """Keep the latest five plans of this session (newest first)."""
    st.session_state.setdefault("plans", [])
    st.session_state["plans"].insert(
        0,
        {
            "title": question.strip().splitlines()[0][:48],
            "at": datetime.now().strftime("%H:%M:%S"),
            "text": answer,
        },
    )
    del st.session_state["plans"][6:]


def saved_titles() -> list[str]:
    """One label per saved run: time · first words of the request."""
    return [
        f"{plan['at']} · {plan['title']}"
        for plan in st.session_state.get("plans", [])
    ]


def reopened_text(title: str) -> str | None:
    """The text of a saved run picked in the sidebar ('(none)' -> None)."""
    titles = saved_titles()
    if title in titles:
        return st.session_state["plans"][titles.index(title)]["text"]
    return None


def make_slug(text: str) -> str:
    """A file name from the plan (like the download name of a good repo)."""
    slug = "".join(
        char.lower() if char.isalnum() else "-" for char in text.strip()[:44]
    )
    return "-".join(part for part in slug.split("-") if part) or "wedding-plan"
