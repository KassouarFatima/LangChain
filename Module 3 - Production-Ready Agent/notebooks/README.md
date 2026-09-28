# 🇩🇿 Module 3 — Notebooks · Production-Ready Agent

**by Kassouar Fatima 🇩🇿 — Module 3 — Production-Ready Agent**

Eight notebooks, taken in order. They build one idea at a time — break the agent,
put a door in front of it, keep the conversation from exploding, then make the
model / prompt / tools **dynamic** — and the last notebook wires every pattern
into a single email agent that ships as the Streamlit app.

---

## 📚 The notebooks

| # | Notebook | What it teaches | Model calls? |
| --- | --- | --- | --- |
| **3_0** | `3_0_Break_it_first_kassouar.ipynb`<br>*Break it first — arrive with your own broken version* | Deliberately break a naive agent, capture **what** failed and **why**, and write the result to `3_0_Break_it_first_results.json`. The pre-work for the whole module. | ✅ yes (~6 min) |
| **3_1** | `3_1_Where_your_agent_needs_a_door_kassouar.ipynb`<br>*Where your agent needs a door* | **Middleware & interrupts**: decide which actions must stop for a human. Reads 3_0's answers file, so **run 3_0 first**. | ❌ no key needed |
| **3_2** | `3_2_Managing_messages_kassouar.ipynb`<br>*Managing messages — summarize and trim* | Long-conversation control: summarization + trimming so the context window never overflows. | ✅ yes (~1 min) |
| **3_3** | `3_3_HITL_kassouar.ipynb`<br>*Human in the loop — approve, reject or edit* | `HumanInTheLoopMiddleware` on a tool: the run **stops**, a human approves / rejects / **edits**, then the run resumes. | ✅ yes (~1 min) |
| **3_4a** | `3_4_Dynamic_models_kassouar.ipynb`<br>*Dynamic models — pick the model per request* | Swap the model **per request**, not per agent. | ✅ yes |
| **3_4b** | `3_4_Dynamic_prompts_kassouar.ipynb`<br>*Dynamic prompts — a system prompt built at call time* | Build the system prompt at **call time** from context (here, the Algerian persona). | ✅ yes |
| **3_4c** | `3_4_Dynamic_tools_kassouar.ipynb`<br>*Dynamic tools — a different toolbox per user role* | Give each **role** its own toolbox — the pattern behind `check_inbox` / `send_email` / `authenticate`. | ✅ yes |
| **3_5** | `3_5_Email_agent_kassouar.ipynb`<br>*Email agent — every Module 3 pattern in one agent* | **Everything combined**: dynamic model + prompt + tools, `InMemorySaver`, `state_schema` / `context_schema`, `HumanInTheLoopMiddleware` on `send_email`. The reference for the app. | ✅ yes (~1 min) |

> The app also ships a runnable copy of 3_5 at
> [`../chatui_emailassistent/streamlit/3.5_email_agent.ipynb`](../chatui_emailassistent/streamlit/3.5_email_agent.ipynb)
> (37 cells, executed top-to-bottom, 0 error cells) — this is the notebook that
> matches the shipped Streamlit code line for line.

---

## ▶️ How to execute

### Fastest way — one double-click per notebook

Each notebook has its own launcher in this folder:

| Runner | Notebook | Jupyter port |
| --- | --- | --- |
| `run_3_0.cmd` | 3_0 Break it first | **8898** |
| `run_3_1.cmd` | 3_1 Where your agent needs a door | **8899** |
| `run_3_2.cmd` | 3_2 Managing messages | **8900** |
| `run_3_3.cmd` | 3_3 Human in the loop | **8901** |
| `run_3_4.cmd` | 3_4 Dynamic models / prompts / tools | **8902** |
| `run_3_5.cmd` | 3_5 Email agent | **8903** |

```powershell
# from this folder
& ".\run_3_0.cmd"
```

A browser tab opens on the notebook → press **Run ▶ → Run All Cells**.
Stop the server with `Ctrl+C` in that window.

### Manual way

```powershell
cd "C:\Users\Kassouar Fatima\Downloads\LangChain\Module 3 - Production-Ready Agent\notebooks"

# Kernel: the course venv — it is the only one with mcp + langchain-mcp-adapters
& "C:\Users\Kassouar Fatima\lca-lc-foundations\.venv\Scripts\python.exe" -m jupyter lab 3_5_Email_agent_kassouar.ipynb --port 8903
```

Then **Kernel → Restart & Run All** (equivalent to running top-to-bottom).

### Requirements

- **`.env`** sits next to these notebooks and already provides
  `GOOGLE_API_KEY` · `GEMINI_API_KEY` · `TAVILY_API_KEY` · `LANGSMITH_*`.
  Every notebook starts with `load_dotenv()`, so **no key is ever typed into a cell**.
- **`resources/`** holds the shared data used by 3_0/3_1.
- **3_1 needs `3_0_Break_it_first_results.json`** — it audits that file. Run **3_0 first**.

---

## ⚠️ Notes when you run them

1. **Use top-level `await`, not `asyncio.run()`** — a Jupyter kernel already has a
   running event loop, so `asyncio.run(...)` raises
   `RuntimeError: asyncio.run() cannot be called from a running event loop`.
   Every async cell in these notebooks is a plain top-level `await`.
2. **Order matters:** `3_0 → 3_1`, and `3_4a/b/c → 3_5`.
3. **Benign stderr warnings** you can ignore: a LangSmith `403` (the free key is
   rejected by the tracing endpoint) and a pydantic `context` serializer warning.
   Neither one affects results — the printed output is what counts.
4. **Expected runtime:** ~6 min for 3_0, ~1 min each for the rest, seconds for 3_1.
5. Notebooks are shipped **with their outputs executed** so you can read the
   results without re-running, but *Run All* reproduces them from scratch.

---

🇩🇿 — **by Kassouar Fatima 🇩🇿** · Module 3 — Production-Ready Agent
