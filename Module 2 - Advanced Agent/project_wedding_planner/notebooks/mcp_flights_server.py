"""MCP server: demo flight search for the DJEF Event & Travel Planner.

Speaks the Model Context Protocol over **stdio** (newline-delimited JSON-RPC),
so any MCP client — the notebook or ``wedding_planner_service`` through
``langchain-mcp-adapters`` — can discover and call its one tool:

    search_flights(origin: str) -> JSON text

The flight rows are a small **demo dataset** (typical diaspora routes into
Algeria), not live prices — the docstring of the tool says so, and every
answer the planner prints repeats it honestly.

Run it by hand to see the protocol live:

    python mcp_flights_server.py      # then type initialize / tools/list JSON

Everything meant for the client goes to **stdout** (the protocol); any note
for the human goes to **stderr** — mixing them would corrupt the stream.
"""
from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

SERVER = FastMCP("djef-flights")

# ---------------------------------------------------------------------------
# Demo data: flights FROM a city (the only parameter the coordinator sends).
# Typical routes guests take to a celebration in Algeria.
# ---------------------------------------------------------------------------
FLIGHTS_BY_ORIGIN = {
    "paris": [
        {"airline": "Air Algérie", "flight": "AH 1081", "route": "Paris CDG -> Algiers",
         "depart": "08:35", "arrive": "10:20", "duration": "1h45", "price_dzd": 38_000},
        {"airline": "Tassili Airlines", "flight": "SF 231", "route": "Paris ORY -> Oran",
         "depart": "11:10", "arrive": "12:55", "duration": "1h45", "price_dzd": 41_500},
        {"airline": "Vueling", "flight": "VY 8861", "route": "Paris CDG -> Algiers",
         "depart": "14:05", "arrive": "15:50", "duration": "1h45", "price_dzd": 34_900},
    ],
    "lyon": [
        {"airline": "Air Algérie", "flight": "AH 1063", "route": "Lyon -> Algiers",
         "depart": "09:50", "arrive": "11:35", "duration": "1h45", "price_dzd": 36_200},
        {"airline": "Transavia", "flight": "TO 7324", "route": "Lyon -> Oran",
         "depart": "16:40", "arrive": "18:25", "duration": "1h45", "price_dzd": 33_400},
    ],
    "marseille": [
        {"airline": "Air Algérie", "flight": "AH 1057", "route": "Marseille -> Algiers",
         "depart": "07:15", "arrive": "08:55", "duration": "1h40", "price_dzd": 35_100},
        {"airline": "Ryanair", "flight": "FR 1121", "route": "Marseille -> Oran",
         "depart": "18:20", "arrive": "20:00", "duration": "1h40", "price_dzd": 29_900},
    ],
    "montreal": [
        {"airline": "Air Algérie", "flight": "AH 403", "route": "Montreal -> Algiers",
         "depart": "21:30", "arrive": "11:15 +1", "duration": "7h45", "price_dzd": 128_000},
        {"airline": "Air Canada", "flight": "AC 78", "route": "Montreal -> Casablanca",
         "depart": "16:05", "arrive": "04:10 +1", "duration": "7h05", "price_dzd": 112_500},
    ],
    "dubai": [
        {"airline": "Emirates", "flight": "EK 751", "route": "Dubai -> Algiers",
         "depart": "14:45", "arrive": "19:30", "duration": "7h45", "price_dzd": 96_000},
        {"airline": "Flydubai", "flight": "FZ 1709", "route": "Dubai -> Oran",
         "depart": "09:20", "arrive": "14:05", "duration": "7h45", "price_dzd": 89_700},
    ],
    "istanbul": [
        {"airline": "Turkish Airlines", "flight": "TK 660", "route": "Istanbul -> Algiers",
         "depart": "12:10", "arrive": "14:05", "duration": "2h55", "price_dzd": 62_300},
        {"airline": "AJet", "flight": "VF 5063", "route": "Istanbul -> Constantine",
         "depart": "17:45", "arrive": "19:35", "duration": "2h50", "price_dzd": 58_900},
    ],
    "london": [
        {"airline": "British Airways", "flight": "BA 8362", "route": "London Heathrow -> Algiers",
         "depart": "10:05", "arrive": "13:55", "duration": "2h50", "price_dzd": 71_400},
        {"airline": "Air Algérie", "flight": "AH 1401", "route": "London Gatwick -> Oran",
         "depart": "13:30", "arrive": "17:20", "duration": "2h50", "price_dzd": 68_800},
    ],
    "rome": [
        {"airline": "ITA Airways", "flight": "AZ 130", "route": "Rome -> Algiers",
         "depart": "09:40", "arrive": "11:30", "duration": "1h50", "price_dzd": 44_600},
    ],
    "madrid": [
        {"airline": "Iberia", "flight": "IB 2306", "route": "Madrid -> Algiers",
         "depart": "12:25", "arrive": "13:55", "duration": "1h30", "price_dzd": 39_800},
    ],
    # Domestic hops inside Algeria (guests coming from another wilaya).
    "algiers": [
        {"airline": "Air Algérie", "flight": "AH 40", "route": "Algiers -> Oran",
         "depart": "07:00", "arrive": "08:05", "duration": "1h05", "price_dzd": 12_400},
        {"airline": "Tassili Airlines", "flight": "SF 5", "route": "Algiers -> Ouargla",
         "depart": "10:30", "arrive": "12:00", "duration": "1h30", "price_dzd": 15_900},
    ],
}

GENERIC_ROUTES = [
    {"airline": "Air Algérie", "flight": "AH 1xxx", "route": "<origin> -> Algiers",
     "depart": "morning", "arrive": "same day", "duration": "varies", "price_dzd": None},
    {"airline": "Turkish Airlines", "flight": "TK 6xx", "route": "<origin> -> Algiers via Istanbul",
     "depart": "evening", "arrive": "next day", "duration": "varies", "price_dzd": None},
]


@SERVER.tool()
def search_flights(origin: str) -> str:
    """Find flights departing from an origin city towards the event in Algeria.

    Args:
        origin: the city guests fly FROM (e.g. 'Paris', 'Lyon', 'Dubai').

    Returns:
        JSON text: the origin, the demo flight rows (airline, flight, route,
        times, indicative price in DA) and an honesty note. The rows come from
        this server's demo dataset — they are not live prices.
    """
    key = str(origin).strip().lower()
    flights = FLIGHTS_BY_ORIGIN.get(key)
    note = "Demo dataset served by the djef-flights MCP server — indicative prices, not a live quote."
    if flights is None:
        known = sorted(FLIGHTS_BY_ORIGIN)
        # Closest match: a known city contained in what the user typed.
        for city, rows in FLIGHTS_BY_ORIGIN.items():
            if city in key or key in city:
                flights, note = rows, note + f" (matched the demo city '{city}'.)"
                break
        else:
            flights, note = GENERIC_ROUTES, (
                f"No demo rows for '{origin}' — showing the two standard ways "
                f"into Algiers. Known demo origins: {', '.join(known)}."
            )
    return json.dumps({"origin": str(origin).strip(), "flights": flights, "note": note},
                      ensure_ascii=False)


if __name__ == "__main__":
    # stdio transport: the protocol runs on stdout, human notes on stderr.
    SERVER.run()
