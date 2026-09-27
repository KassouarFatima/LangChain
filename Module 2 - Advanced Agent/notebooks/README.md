# 🇩🇿 Module 2 — Notebooks · Advanced Agent

**by Kassouar Fatima 🇩🇿 — Module 2 — Advanced Agent**

Four notebooks. They continue exactly where Module 1 stopped — same style, same
model, same setup — and add the tool that makes agents *advanced*: **MCP (Model
Context Protocol)**, then state, runtime context and specialist sub-agents.

---

## 📚 The notebooks

| # | Notebook | Title | What you learn | API key |
| --- | --- | --- | --- | --- |
| **2_1** | `2_1_MCP_kassouar.ipynb` | *Advanced agents — MCP (Model Context Protocol)* | Expose **tools, resources and prompts** through an MCP server; an agent consumes them over local *stdio* **and** online | `GOOGLE_API_KEY` |
| **2_1+2_2** | `2_1_2_2_Travel_State_Context_kassouar.ipynb` | *Advanced agents — Travel agent (MCP), State & Runtime Context* | Connect to a **public MCP server** over HTTP (Kiwi flight search); add **state fields** tools write with `Command`; pass per-run **runtime context** typed with `context_schema` | `GOOGLE_API_KEY` |
| **2_3** | `2_3_Multi_agent_kassouar.ipynb` | *Advanced agents — Multi-agent (subagents)* | Split the work: tiny **specialist sub-agents** each own one tool, a **main agent** delegates through `@tool` wrappers calling `subagent.invoke(...)` | `GOOGLE_API_KEY` |
| **project** | `wedding_planner_kassouar.ipynb` | *Wedding planner — an Algerian wedding* | The module project in notebook form: a **Coordinator** dispatching to ✈️ Flights (MCP) · 🏛️ Venue (web search) · 🎵 Playlist (SQLite/SQL) | `GOOGLE_API_KEY` |

**Supporting files**

```
notebooks/
├── 2_1_MCP_kassouar.ipynb
├── 2_1_2_2_Travel_State_Context_kassouar.ipynb
├── 2_3_Multi_agent_kassouar.ipynb
├── wedding_planner_kassouar.ipynb
├── .env                        ← GOOGLE_API_KEY / GEMINI_API_KEY / LANGSMITH_*
├── resources/
│   └── 2_1_mcp_server.py       ← the local MCP server launched by lesson 2_1
└── project_wedding_planner/notebooks/   ← the project's own bench notebook
    ├── wedding_planner_kassouar.ipynb
    ├── wedding_planner_service.py       ← Coordinator + 3 specialists
    └── mcp_flights_server.py            ← local flights MCP server (stdio)
```

---

## ▶️ How to execute

This module ships **no `.cmd` launchers** — start Jupyter yourself:

```powershell
# 1. environment (once) — same venv as Module 1
uv pip install --python ".venv\Scripts\python.exe" `
    langchain langchain-google-genai langchain-mcp-adapters mcp-server-time python-dotenv

# 2. keys: copy .env.example to .env and add GOOGLE_API_KEY

# 3. open a notebook
cd "C:\Users\Kassouar Fatima\Downloads\LangChain\Module 2 - Advanced Agent\notebooks"
& "C:\Users\Kassouar Fatima\Downloads\LangChain\Module 1 - Create Agent\djef_chef\.venv\Scripts\python.exe" -m jupyter lab 2_1_MCP_kassouar.ipynb
```

In Jupyter: **Kernel → Restart & Run All** (equivalent to running top-to-bottom).

### For the project's own notebook

```powershell
cd "C:\Users\Kassouar Fatima\Downloads\LangChain\Module 2 - Advanced Agent\project_wedding_planner"
& ".\run_notebook.cmd"        # its own launcher
```

---

## ⚠️ Notes when you run them

1. **Take them in order** `2_1 → 2_1+2_2 → 2_3 → wedding_planner`.
   `2_1` introduces the MCP server that `2_1+2_2` reuses over HTTP.
2. **`resources/2_1_mcp_server.py` must stay next to notebook 2_1** — that notebook
   launches it as a local *stdio* MCP server.
3. **The travel notebook needs internet** — it reaches the public
   `https://mcp.kiwi.com` server. No extra key, but a connection is required.
4. **`.env` lives in this folder** and already provides `GOOGLE_API_KEY`,
   `GEMINI_API_KEY` and the optional `LANGSMITH_*` values. Every notebook starts
   with `load_dotenv()` — **no key is ever typed into a cell**, and `.env` is
   git-ignored.
5. **Benign stderr warnings** you can ignore: a LangSmith `403` (free key rejected
   by the tracing endpoint) and pydantic `context` serializer warnings. Neither
   affects the printed results.
6. All four notebooks ship **executed with 0 error cells**, so you can read the
   results without re-running — but **Restart & Run All** reproduces them.

---

## ➡️ What comes next

`wedding_planner_kassouar.ipynb` becomes the module project:

→ **[`../project_wedding_planner/README.md`](../project_wedding_planner/README.md)**
— the DJEF Wedding app (Coordinator + 3 specialists), its screenshots, tests and
deploy steps.

---

🇩🇿 **Mabrouk!** — **by Kassouar Fatima 🇩🇿** · Module 2 — Advanced Agent
