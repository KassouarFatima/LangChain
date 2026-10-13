# 🇩🇿 DJEF Wedding — Notebook

**by Kassouar Fatima 🇩🇿 — Module 2 — Advanced Agent · project notebook**

One notebook that **builds and benches the whole project**: a Coordinator that
delegates to three specialists — ✈️ **Flights** (local MCP server) · 🏛️ **Venue**
(live web search) · 🎵 **Playlist** (SQLite over SQL) — then exercises every path
and prints a trace.

---

## 📚 What's in this folder

| File | What it is |
| --- | --- |
| `wedding_planner_kassouar.ipynb` | **The notebook** — 25 cells (13 markdown · 12 code), shipped executed with **0 error cells** |
| `wedding_planner_service.py` | The **Coordinator + 3 specialists** the notebook imports |
| `mcp_flights_server.py` | The **local flights MCP server** (stdio) the Coordinator talks to |
| `data/playlist.db` | The **playlist database** (SQLite, ~12 KB) used by the 🎵 Playlist specialist |
| `data/playlist.db.pre-break.bak` | Backup of that database, taken before a deliberate break-it-first exercise |

The notebook runs a bench over: **MCP · SQL · delegation · tests · trace**.

---

## ▶️ How to execute

### Fastest way — one double-click

```powershell
# from the project folder (one level up)
& ".\run_notebook.cmd"
```

- Opens **Jupyter Lab on port 8892** with this folder.
- Open `wedding_planner_kassouar.ipynb`, then press **Run ▶ → Run All Cells**.
- Kernel: the `Personal Algerian Chef` `.venv` (Python 3.13) — **the key loads
  automatically** from the project's `.env`.
- Stop the server with `Ctrl+C` in that window.

### Manual way

```powershell
cd "C:\Users\Kassouar Fatima\Downloads\LangChain\Module 2 - Advanced Agent\project_wedding_planner\notebooks"

& "C:\Users\Kassouar Fatima\Downloads\courses\Personal Algerian Chef\.venv\Scripts\python.exe" -m jupyter lab wedding_planner_kassouar.ipynb --port 8892
```

Then **Kernel → Restart & Run All** (equivalent to running top-to-bottom).

> Prefer the module-level notebook instead? See
> [`../../notebooks/README.md`](../../notebooks/README.md) — that folder holds the
> four lesson notebooks.

---

## ⚠️ Notes when you run it

1. **Keep this folder intact** — the notebook imports `wedding_planner_service`
   from here, launches `mcp_flights_server.py` as a local *stdio* MCP server, and
   opens `data/playlist.db`. Run it from **this** directory.
2. **`.env` sits one level up** (project root). The launcher pre-loads it, so no
   key is ever typed into a cell. `.env` is git-ignored.
3. **The flights specialist needs internet** for its live-search path; the local
   MCP server itself runs offline.
4. **`data/playlist.db` is created/seeded on first run** if it's missing —
   `ensure_playlist_db()` handles that (the app launcher calls it too).
5. **Benign stderr warnings** you can ignore: a LangSmith `403` (free key rejected
   by the tracing endpoint) and pydantic serializer warnings.
6. Shipped **with outputs** (0 error cells) so you can read the bench without
   re-running — **Restart & Run All** reproduces it.

---

## ➡️ What comes next

The notebook is the lab; the app is the product:

| Entry point | Command |
| --- | --- |
| This notebook | `& ".\run_notebook.cmd"` → Run All Cells |
| The Streamlit app | `& ".\run_app.cmd"` → `http://localhost:8511` |
| Full docs + screenshots | **[`../README.md`](../README.md)** |

---

🇩🇿 **Mabrouk!** — **by Kassouar Fatima 🇩🇿** · Module 2 — Advanced Agent
