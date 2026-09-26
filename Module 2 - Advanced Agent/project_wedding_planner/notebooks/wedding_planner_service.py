"""DJEF Wedding — shared service for the Module 2 project.

The Coordinator team (lesson 2_3 wiring): one **Coordinator Agent** that never
does the work itself, delegating to **three specialists**, each hidden behind
an ordinary ``@tool`` wrapper:

| specialist | its real tool | parameter mapping |
|---|---|---|
| flights  | ``search_flights`` via a **local MCP server** (stdio) | `Origin` |
| venue    | ``web_search`` (Tavily, live web)                   | `Destination`, `Guest_Count` |
| playlist | ``run_sql`` (SELECT over a local **SQLite** database) | `Genre` |

Both the notebook ``notebooks/wedding_planner_kassouar.ipynb`` and the app
``streamlit/app.py`` import this module, so the agents and tools stay in one
place. The coordinator prompt is the "Coordinator Agent" ROLE spec verbatim,
plus the bridge section that binds it to the three ``ask_*`` tools.

Honesty rules baked into the tools: flight rows are a **demo dataset** served
by the MCP server (not live prices), venue results are live web results with
their links, and the playlist comes from the local teaching database.
"""
from __future__ import annotations

import asyncio
import json
import os
import sqlite3
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import tool

EVENT_MODEL = os.getenv("EVENT_MODEL", "google_genai:gemini-3.1-flash-lite")
# Old name kept so nothing that still imports it keeps working.
WEDDING_MODEL = EVENT_MODEL

# The MCP server (one process, stdio transport) and the SQLite database live
# next to this file, so they resolve no matter where Jupyter/app was started.
MCP_SERVER_PATH = Path(__file__).resolve().parent / "mcp_flights_server.py"
PLAYLIST_DB_PATH = Path(__file__).resolve().parent / "data" / "playlist.db"

# ---------------------------------------------------------------------------
# The budget range — the condition that keeps the sidebar's "Budget limit (DA)"
# fit for the model: 0 means "no limit", anything else must sit between
# BUDGET_MIN_VALID and BUDGET_MAX (values like 50, 100 or 500 are rejected).
# ---------------------------------------------------------------------------
BUDGET_MIN_VALID = 100_000
BUDGET_MAX = 3_000_000
BUDGET_STEP = 50_000


def valid_budget(value: object) -> bool:
    """True when a ceiling fits the range the model can reason about:
    0 (= no limit) or 100 000 – 3 000 000 DA."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return False
    return value == 0 or BUDGET_MIN_VALID <= value <= BUDGET_MAX


# ---------------------------------------------------------------------------
# Keys (same rule as every notebook in this path: .env, never inside the code)
# ---------------------------------------------------------------------------
def _pull_streamlit_secrets() -> None:
    """Streamlit Community Cloud keeps the keys in the app's Secrets store —
    no .env file travels with the repo. Copy any secret into the environment,
    but only when it is not already set, so the local .env always wins."""
    try:
        import streamlit as st  # only importable inside the app runtime

        for key, value in st.secrets.items():
            if key and str(value).strip() and key not in os.environ:
                os.environ[key] = str(value)
    except Exception:
        # Not running under Streamlit, or no secrets configured — fine locally.
        pass


def load_keys() -> str:
    """Load the Gemini key from the nearest .env; returns where it came from.

    Looks next to the current folder first, then next to this file (the
    project folder) — so it works no matter where Jupyter was started.
    On Streamlit Community Cloud the Secrets store is consulted as well.
    """
    _pull_streamlit_secrets()
    module_dir = Path(__file__).resolve().parent
    for candidate in (
        Path.cwd() / ".env",
        Path.cwd().parent / ".env",
        module_dir / ".env",
        module_dir.parent / ".env",
    ):
        if candidate.exists():
            load_dotenv(candidate, override=True)
            return str(candidate)
    load_dotenv(override=True)
    if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
        # Only prompt on a real terminal (Jupyter/console); never block a
        # Streamlit Cloud run, where stdin is not an interactive terminal.
        if not (getattr(sys.stdin, "isatty", lambda: False)()):
            return "environment"
        import getpass

        key = getpass.getpass("Gemini key (GOOGLE_API_KEY): ").strip()
        if key:
            os.environ["GOOGLE_API_KEY"] = key
            return "typed"
    return "environment"


# ---------------------------------------------------------------------------
# Tool 1 (MCP): the Flights Agent's tool, discovered from the server
# ---------------------------------------------------------------------------
def _to_sync(coro: object) -> object:
    """Run the async MCP adapter in a plain sync context.

    ``langchain-mcp-adapters`` is async; the notebook, the agent tools and
    Streamlit are sync. When no loop is running we simply ``asyncio.run`` —
    and if we ever get called *inside* a running loop, a fresh thread with
    its own loop does it (never nest loops).
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result(timeout=60)


def flights_mcp_tools() -> list:
    """Ask the djef-flights MCP server which tools it exposes (stdio).

    The adapter's tools are async-only, while our agent — Streamlit and the
    notebook included — is sync; every discovered tool therefore comes back
    with a sync twin (same name, schema and behaviour) via ``_sync_view``.
    """
    from langchain_mcp_adapters.client import MultiServerMCPClient

    client = MultiServerMCPClient(
        {
            "flights": {
                "command": sys.executable,           # the same Python as us
                "args": [str(MCP_SERVER_PATH)],      # python mcp_flights_server.py
                "transport": "stdio",                # JSON-RPC over stdin/stdout
            }
        }
    )
    return [_sync_view(mcp_tool) for mcp_tool in _to_sync(client.get_tools())]


def _sync_view(mcp_tool: object) -> object:
    """A sync twin of an async-only MCP tool (same name, schema, answers)."""
    from langchain_core.tools import StructuredTool

    args_schema = getattr(mcp_tool, "args_schema", None)
    if args_schema is None:  # the adapter always ships one — fail loudly if not
        raise RuntimeError(f"MCP tool '{mcp_tool.name}' has no args schema")

    def _run(**kwargs: object) -> str:
        return _mcp_text(_to_sync(mcp_tool.ainvoke(kwargs)))

    return StructuredTool(
        name=mcp_tool.name,
        description=mcp_tool.description,
        args_schema=args_schema,
        func=_run,
    )


def _mcp_text(result: object) -> str:
    """MCP answers arrive as content blocks — pull the text out of them."""
    if isinstance(result, str):
        return result
    if isinstance(result, list):
        parts = [
            block.get("text", "")
            for block in result
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        if parts:
            return "\n".join(parts)
    return str(result)


# ---------------------------------------------------------------------------
# Tool 2 (SQL): the Playlist Agent's tool, over a local SQLite database
# ---------------------------------------------------------------------------
# A small teaching playlist: (title, artist, genre, seconds).
PLAYLIST_SEED = [
    ("Didi", "Khaled", "rai", 252),
    ("Aïcha", "Khaled", "rai", 276),
    ("Lili Twil", "Cheb Hasni", "rai", 301),
    ("Baroud", "Cheb Hasni", "rai", 288),
    ("Ghorba", "Cheb Bilal", "rai", 264),
    ("Ya Rayah", "Dahmane El Harrachi", "chaabi", 318),
    ("Nuit d'Alger", "Orchestre El Djazaïr", "chaabi", 274),
    ("Zina", "Group El Draâ", "chaabi", 245),
    ("Bab El Ghorba", "Mahmoud Benali", "chaabi", 296),
    ("Lila", "Ensemble Andalou de Tlemcen", "andalous", 340),
    ("Nassam Alayna El Hawa", "Mohamed El Anka", "andalous", 355),
    ("Sahra", "Ensemble Andalou d'Alger", "andalous", 322),
    ("A Vava Inouva", "Idir", "kabyle", 268),
    ("Ddunit", "Idir", "kabyle", 284),
    ("Lizebrag Tiziri", "Larbi Batma", "kabyle", 306),
    ("Azul", "Souad Massi", "kabyle", 259),
    ("Mahmouda", "Rachid Taha", "melhoun", 247),
    ("Tirir", "Cheb Mami", "melhoun", 262),
    ("Bsat Lhem", "Fadela Dziria", "melhoun", 331),
    ("Parisiana", "Cheb Mami", "pop", 258),
    ("Madaniti", "Cheb Mami", "pop", 241),
    ("Voilà Voilà", "Faudel", "pop", 233),
    ("Beb Waneh", "Rachid Taha", "pop", 249),
    ("Dima", "Soolking", "rap", 221),
    ("Algérie", "Soolking", "rap", 236),
    ("Casanova", "Kery James", "rap", 254),
    ("Le Fleuve", "DJ Mounir", "electro", 275),
    ("Sahara Nights", "Rachid DJ", "electro", 302),
]
GENRES = ["chaabi", "rai", "andalous", "kabyle", "melhoun", "pop", "rap", "electro"]


def _open_playlist() -> sqlite3.Connection:
    """Open the playlist database read-write; on a read-only checkout fall
    back to a read-only connection.

    Streamlit Community Cloud ships the repository inside a read-only
    checkout — the seeded ``playlist.db`` is then used exactly as it is in
    git (28 rows), while locally the same file can still be created/seeded.
    """
    con = None
    try:
        con = sqlite3.connect(PLAYLIST_DB_PATH)
        con.execute("PRAGMA user_version")  # force the file to open right now
        return con
    except sqlite3.Error:
        if con is not None:
            try:
                con.close()
            except Exception:
                pass
        return sqlite3.connect(f"file:{PLAYLIST_DB_PATH}?mode=ro", uri=True)


def ensure_playlist_db() -> dict:
    """Create the playlist database with its demo rows if it is not there yet.

    The notebook shows the SQL by hand; this function only guarantees the app
    finds the same database on a fresh checkout. On a read-only checkout
    (Streamlit Community Cloud) the writes are skipped and the rows already
    shipped in git are used as they are.
    """
    created = not PLAYLIST_DB_PATH.exists()
    try:
        PLAYLIST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass  # read-only checkout — the seeded file must already be there
    try:
        with _open_playlist() as con:
            con.execute(
                "CREATE TABLE IF NOT EXISTS tracks ("
                " id INTEGER PRIMARY KEY AUTOINCREMENT,"
                " title TEXT NOT NULL,"
                " artist TEXT NOT NULL,"
                " genre TEXT NOT NULL,"
                " duration_sec INTEGER NOT NULL)"
            )
            count = con.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
            if count == 0:
                con.executemany(
                    "INSERT INTO tracks (title, artist, genre, duration_sec)"
                    " VALUES (?, ?, ?, ?)",
                    PLAYLIST_SEED,
                )
                count = len(PLAYLIST_SEED)
    except sqlite3.Error:
        # Read-only filesystem: use the shipped, already-seeded database.
        with _open_playlist() as con:
            count = con.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
        created = False
    return {"path": str(PLAYLIST_DB_PATH), "created": created, "tracks": count}


@tool
def run_sql(query: str) -> str:
    """Run a SELECT query on the playlist database (the Playlist Agent's SQL tool).

    The only table is ``tracks(id, title, artist, genre, duration_sec)`` —
    genres: chaabi, rai, andalous, kabyle, melhoun, pop, rap, electro.
    Example: SELECT title, artist, duration_sec FROM tracks WHERE genre LIKE
    '%chaabi%' LIMIT 10. Only SELECT/WITH statements are allowed; other
    statements are refused. Returns the columns and the first 50 rows as JSON.
    """
    ensure_playlist_db()
    sql = str(query).strip()
    if not sql:
        return json.dumps({"error": "Empty query — send a SELECT."}, ensure_ascii=False)
    first = sql.split(None, 1)[0].lower().rstrip(";")
    if first not in {"select", "with"}:
        return json.dumps(
            {"error": "Only SELECT queries are allowed on this database.",
             "query": sql},
            ensure_ascii=False,
        )
    try:
        with _open_playlist() as con:
            con.row_factory = sqlite3.Row
            rows = [dict(row) for row in con.execute(sql).fetchmany(50)]
    except sqlite3.Error as exc:
        return json.dumps({"error": f"SQL error: {exc}", "query": sql},
                          ensure_ascii=False)
    return json.dumps(
        {"query": sql, "row_count": len(rows), "rows": rows,
         "note": "Local teaching playlist database (demo rows)."},
        ensure_ascii=False,
    )


# ---------------------------------------------------------------------------
# Tool 3 (Web Search): the Venue Agent's tool — live results, honest fallbacks
# ---------------------------------------------------------------------------
@tool
def web_search(query: str) -> str:
    """Live web search (Tavily) — the Venue Agent's tool for current venues.

    Pass one targeted query containing the destination and the capacity,
    e.g. "event venue hire Algiers capacity 300 guests price". Returns a few
    short results with their links; without the Tavily key (or during an
    outage) it returns a friendly message instead of failing.
    """
    try:
        from tavily import TavilyClient
    except ImportError:
        return json.dumps(
            {"query": query,
             "message": "Live search is not installed (pip install tavily-python) "
                        "— answer with what you know and say research is off."},
            ensure_ascii=False,
        )
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return json.dumps(
            {"query": query,
             "message": "Live search is not configured (TAVILY_API_KEY missing "
                        "from the .env) — answer with what you know and say so."},
            ensure_ascii=False,
        )
    try:
        raw = TavilyClient(api_key=api_key).search(query.strip(), max_results=4)
    except Exception as exc:  # a temporary outage — the agent explains it
        return json.dumps(
            {"query": query,
             "message": f"Live search unavailable right now ({type(exc).__name__}) "
                        "— answer with what you know and say so."},
            ensure_ascii=False,
        )
    results = [
        {
            "title": str(item.get("title", "")),
            "url": str(item.get("url", "")),
            "snippet": str(item.get("content", ""))[:220],
        }
        for item in raw.get("results", [])[:4]
    ]
    return json.dumps({"query": query, "results": results}, ensure_ascii=False)


# ---------------------------------------------------------------------------
# The team: one coordinator + three specialists behind @tool wrappers
# ---------------------------------------------------------------------------
# What each specialist owns — for the notebook, the README and the trace.
SPECIALISTS = {
    "flights": ["search_flights (MCP server)"],
    "venue": ["web_search (live web search)"],
    "playlist": ["run_sql (SQL query)"],
}
COORDINATOR_TOOLS = ["ask_flights", "ask_venues", "ask_playlist"]
PLANNER_TOOLS = COORDINATOR_TOOLS  # old name, still importable

FLIGHTS_SPECIALIST_PROMPT = """You are the Flights Agent of the DJEF travel &
event team (Tool: MCP Server).
- You receive ONE parameter: `Origin` — the city guests fly FROM.
- Call search_flights(origin) exactly once, passing that city as given; the
  tool answers from the djef-flights MCP server's demo dataset.
- Report each flight as one short line: airline · flight · route · times ·
  indicative price in DA — and repeat the tool's honesty note (demo data, not
  a live quote). Never invent a flight, a time or a price.
- Short English lines; no greetings."""

VENUE_SPECIALIST_PROMPT = """You are the Venue Agent of the DJEF travel & event
team (Tool: Web Search).
- You receive TWO parameters: `Destination` (the event city) and `Guest_Count`
  (how many people attend).
- Call web_search with ONE query that contains both, e.g.
  "event venue hire <destination> capacity <n> guests price".
- From the results, pick the venues that fit the capacity: report name, what
  the snippet says (capacity, price if present) and its URL. Never invent a
  venue or a URL; if the tool says research is unavailable, say so in one line.
- Short English lines; no greetings."""

PLAYLIST_SPECIALIST_PROMPT = """You are the Playlist Agent of the DJEF travel &
event team (Tool: SQL Query).
- You receive ONE parameter: `Genre` — the music style for the party.
- The table is tracks(id, title, artist, genre, duration_sec); genres:
  chaabi, rai, andalous, kabyle, melhoun, pop, rap, electro.
- Call run_sql with a SELECT that filters on the genre, e.g.
  SELECT title, artist, duration_sec FROM tracks WHERE genre LIKE '%<genre>%'
  LIMIT 10. If the genre is unknown, first run
  SELECT genre, COUNT(*) AS n FROM tracks GROUP BY genre and pick the closest.
- Present the rows as a numbered playlist with artists and durations; never
  invent a row. Short English lines; no greetings."""

COORDINATOR_PROMPT = """# ROLE
You are the "Coordinator Agent," the central orchestrator for a multi-agent
travel and event planning system. Your job is to analyze user requests,
extract specific parameters, delegate tasks to specialized sub-agents, and
compile the final response.

# INPUT PARAMETERS TO EXTRACT
Whenever a user makes a request, you must extract the following variables:
- `Origin`: The starting location for flights.
- `Destination`: The location of the event/venue.
- `Guest_Count`: The number of people attending.
- `Genre`: The type of music or vibe for the playlist.

# SUB-AGENTS & TOOLS
You manage three specialized worker agents. You must route the extracted
parameters to them according to the strict mapping below:

1. **Flights Agent** (Tool: MCP Server)
   - **Parameter mapping:** `Origin`
   - **Task:** Retrieve flight information based on the origin.
2. **Venue Agent** (Tool: Web Search)
   - **Parameter mapping:** `Destination`, `Guest_Count`
   - **Task:** Search the web for suitable venues based on location and capacity.
3. **Playlist Agent** (Tool: SQL Query)
   - **Parameter mapping:** `Genre`
   - **Task:** Query the database to generate or retrieve a playlist matching
     the requested genre.

# WORKFLOW
When a user provides a prompt, follow these steps:
1. **Analyze & Extract:** Read the user's request and extract the 4 parameters
   (`Origin`, `Destination`, `Guest_Count`, `Genre`).
2. **Validate:** If any required parameter is missing, ask the user to provide
   the missing information before proceeding.
3. **Dispatch:** Trigger the sub-agents in parallel or sequentially, passing
   only the required parameters to each.
   - Call `Flights Agent` with `Origin`.
   - Call `Venue Agent` with `Destination` and `Guest_Count`.
   - Call `Playlist Agent` with `Genre`.
4. **Synthesize:** Wait for all sub-agents to return their results. Compile
   the flight options, venue recommendations, and playlist into a single,
   cohesive, and well-formatted response for the user.

# RESPONSE FORMAT
Your final output to the user should be structured clearly:
- ✈️ **Flights:** [Results from Flights Agent]
- 🏛️ **Venue:** [Results from Venue Agent]
- 🎵 **Playlist:** [Results from Playlist Agent]

# HOW YOU DISPATCH — your three actual tools
Workflow step 3 runs through the tools on your list. Call each with ONLY its
mapped parameters, several in the same turn, wait for their answers, then
synthesize:
- `ask_flights(origin)` — the Flights Agent (MCP server).
- `ask_venues(destination, guest_count)` — the Venue Agent (web search).
- `ask_playlist(genre)` — the Playlist Agent (SQL query).

The request may also carry extra wedding facts (style, date, budget_limit,
priorities). Use them to enrich the answer — a budget to weigh venues with, a
style and a date to shape the plan — but dispatch on the four parameters only.

VOICE
- Reply in English, warm and concise.
- If asked what you are, one short line ("DJEF Wedding — a planner and her
  specialists") and straight back to the plan.
- Repeat the tools' honesty notes (demo flights, indicative prices, research
  availability) — never hide them."""


def build_event_agent(model: str | None = None) -> object:
    """The team: one coordinator + three subagents (lesson 2_3 wiring).

    Each specialist is a normal ``create_agent`` with its own real tool (MCP /
    web search / SQL) and hides behind an ordinary ``@tool`` wrapper that runs
    ``subagent.invoke(...)`` — the coordinator never knows it talks to agents.
    """
    model = model or EVENT_MODEL

    flights_agent = create_agent(
        model=model,
        tools=flights_mcp_tools(),          # discovered live from the MCP server
        system_prompt=FLIGHTS_SPECIALIST_PROMPT,
    )
    venue_agent = create_agent(
        model=model,
        tools=[web_search],
        system_prompt=VENUE_SPECIALIST_PROMPT,
    )
    playlist_agent = create_agent(
        model=model,
        tools=[run_sql],
        system_prompt=PLAYLIST_SPECIALIST_PROMPT,
    )

    def delegate(agent_obj: object, request: str) -> str:
        """The bridge: run a subagent, return its last message as plain text."""
        response = agent_obj.invoke(
            {"messages": [HumanMessage(content=request)]}
        )
        return last_text(response)

    @tool
    def ask_flights(origin: str) -> str:
        """Dispatch the Flights Agent (MCP server). Parameters: only `origin`
        — the city guests fly FROM (e.g. 'Paris')."""
        return delegate(flights_agent, f"Origin: {origin}")

    @tool
    def ask_venues(destination: str, guest_count: int) -> str:
        """Dispatch the Venue Agent (live web search). Parameters: only
        `destination` (event city) and `guest_count` (number attending)."""
        return delegate(
            venue_agent,
            f"Destination: {destination}\nGuest_Count: {guest_count}",
        )

    @tool
    def ask_playlist(genre: str) -> str:
        """Dispatch the Playlist Agent (SQL query). Parameters: only `genre`
        — the music style for the party (e.g. 'chaabi')."""
        return delegate(playlist_agent, f"Genre: {genre}")

    return create_agent(
        model=model,
        tools=[ask_flights, ask_venues, ask_playlist],
        system_prompt=COORDINATOR_PROMPT,
    )


def last_text(response: object) -> str:
    """Last message as plain text (Gemini content may be a list of blocks)."""
    msg = response["messages"][-1]
    content = msg.content
    if isinstance(content, str):
        return content
    if content and isinstance(content, list):
        return content[0].get("text", "")
    return str(content)
