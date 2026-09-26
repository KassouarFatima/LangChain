# 🧪 DJEF Wedding — test cases

> **App:** `streamlit/app.py` (coordinator + 3 specialists) · **Port:** 8511
> **Preconditions:** `.env` with `GOOGLE_API_KEY` (+ `TAVILY_API_KEY`) · double-click
> `run_app.cmd` · browser opens `http://localhost:8511`
> **How to fill Result:** put **✔** = works as expected, **✗** = failed + one line
> of what happened instead. Cases marked ✔ were already verified automatically.

| ID | Case | Steps & input (already filled) | Expected result | Result |
|---|---|---|---|---|
| **TC-01** | Launch + DB direct connection | Double-click `run_app.cmd` | Console prints `[DB] direct connection OK -> …\data\playlist.db` and `tracks: 28`; browser opens; no error/traceback | ✔ |
| **TC-02** | UI — old sidebar kept, new inputs added | Just look at the sidebar | guests **100** · Wilaya **Alger** · Style **simple** · date · budget **0** · priorities **[Traiteur & menu, Photo & video]** · **Origin = Paris** · **Playlist genre = Chaabi**; byline *by Kassouar Fatima* on top; title **💍 DJEF Wedding — Algerian wedding planner** | ✔ |
| **TC-03** | Dark / light switch | Click **🌙 Dark mode**, then **☀️ Light mode** | Whole page turns dark (navy `#0B1220`), button flips label; second click returns to light — no error | ✔ |
| **TC-04** | Sample brief fills the box | Click **Load sample brief** | Request box filled with the Tlemcen wedding text (contains *Paris* and *chaabi*) | ✔ |
| **TC-05** | **Full dispatch — 4 parameters** | Keep the sidebar defaults; click **Load sample brief** → **Prepare the plan 💍** | After ~20–40 s one English answer with **three sections**: ✈️ **Flights** (airlines, times, DA prices + “demo dataset” note) · 🏛️ **Venue** (venues + real links) · 🎵 **Playlist** (numbered tracks with artists) | ✔ |
| **TC-06** | Validation — missing parameters | Clear the box, type `Find me a nice venue in Oran.` → Prepare | The coordinator **asks** for the missing Origin / Guest count / Genre instead of answering | ✔ |
| **TC-07** | Venue = live web search | Sidebar guests **300**, Wilaya **Alger**; type `Give me the venue options in Algiers for 300 guests.` | Real venue results **with URLs** (needs `TAVILY_API_KEY`), or one honest line “live search is not configured” — URLs are never invented | ✔ |
| **TC-08** | Playlist = SQL over the DB | Type `Only the playlist: a rai list for the party.` | Numbered rai list **from the database** (Didi, Aïcha, Lili Twil… with artists) + database note | ✔ |
| **TC-09** | Flights = MCP server, honest demo data | Type `Origin: Paris — which flights can our guests take?` | Flights from the MCP demo dataset (Air Algérie AH 1081, …) with prices in DA and the **“not a live quote”** note | ✔ |
| **TC-10** | Unknown origin — graceful fallback | Type `Origin: Tombouctou — flights please.` (with the other 3 parameters) | Friendly fallback listing the known demo origins — **no crash** | ✔ |
| **TC-11** | SQL safety — writes refused | Notebook, section 3: `wp.run_sql.invoke({"query": "DELETE FROM tracks"})` | Answer: `Only SELECT queries are allowed on this database.` — rows unchanged | ✔ |
| **TC-12** | Saved runs + download | After TC-05: click **Download this plan (.md)**, then reopen the run under **Saved runs** | A `.md` file downloads; the saved run reopens with its answer | _(fill)_ |
| **TC-13** | Notebook — full bench | Double-click `run_notebook.cmd` → **Run All Cells** | **25 cells, 0 errors**; §1 MCP flights, §2 live venues, §3 CREATE/rows/refused-write, §5 team, §6 ✈️🏛️🎵, §7 validation, §8 trace with `ask_*`; quota waits print `quota hit — waiting…` instead of failing | ✔ |
| **TC-14** | Wrong environment guard | (optional) start the app with Anaconda Python | Blue friendly message “Wrong Python environment…” — no traceback | _(fill)_ |
| **TC-15** | Budget limit — range condition | Sidebar → **Budget limit (DA)**: try `0`, then `500`, then `800000` | `0` → blue info *“0 = no limit … a real budget sits between 100 000 and 3 000 000 DA”*; `500` → yellow warning *“outside the valid range … will not be sent to the model”*; `800000` → **no** message | ✔ |

**Summary:** ___ passed · ___ failed — **Tested by:** Kassouar Fatima 🇩🇿 — date: ______
