# 🇩🇿 Module 1 — Notebooks · Create Agent

**by Kassouar Fatima 🇩🇿 — Module 1 — Create Agent**

Four lessons, taken in order. Each one adds one capability, and the end-of-module
project (**DJEF — Personal Algerian Chef**) combines all four.

---

## 📚 The notebooks

| # | Notebook | Title | What you learn | API key |
| --- | --- | --- | --- | --- |
| **1_1** | `1_1_Creation_Agent_foundational_models_kassouar.ipynb` | *Foundational models with LangChain* | Call a model (Gemini / Ollama), wrap it in an agent, control temperature / tokens / retries, streaming | `GOOGLE_API_KEY` |
| **1_2** | `1_2_Tools_and_web_search_kassouar.ipynb` | *Tools and web search for agents* | Give the agent tools: Python functions + **web search** (Tavily) — the *Action → Observation* loop | `GOOGLE_API_KEY` + `TAVILY_API_KEY` |
| **1_3** | `1_3_Short_term_memory_kassouar.ipynb` | *Short-term memory for agents* | The forgetting problem, the **checkpointer**, the **thread id** | `GOOGLE_API_KEY` |
| **1_4** | `1_4_Multimodal_messages_kassouar.ipynb` | *Multimodal messages for agents* | Send **image + audio** to the same agent (content blocks, base64, `mime_type`) | `GOOGLE_API_KEY` |

**Supporting files**

```
notebooks/
├── 1_1 … 1_4  *_kassouar.ipynb   the four lessons
├── run_1_1.cmd … run_1_4.cmd     one launcher per notebook
└── assets/                       used by lesson 1_4
    ├── banner_dark_pink_contacts.png
    └── liecio-calming-rain-257596.mp3
```

---

## ▶️ How to execute

### Fastest way — one double-click per notebook

| Runner | Notebook | Jupyter port |
| --- | --- | --- |
| `run_1_1.cmd` | 1_1 Foundational models | **8891** |
| `run_1_2.cmd` | 1_2 Tools and web search | **8893** |
| `run_1_3.cmd` | 1_3 Short-term memory | **8894** |
| `run_1_4.cmd` | 1_4 Multimodal messages | **8895** |

```powershell
# from this folder
& ".\run_1_1.cmd"
```

A browser tab opens on the notebook → press **Run ▶ → Run All Cells**.
Stop the server with `Ctrl+C` in that window.

> Each launcher uses the **`djef_chef\.venv`** kernel (Python 3.13) and pre-loads
> the keys from **`djef_chef\.env`** before Jupyter starts — so no key is ever
> typed into a cell.

### Manual way

```powershell
cd "C:\Users\Kassouar Fatima\Downloads\LangChain\Module 1 - Create Agent\notebooks"
& "..\djef_chef\.venv\Scripts\python.exe" -m jupyter lab 1_1_Creation_Agent_foundational_models_kassouar.ipynb --port 8891
```

Then **Kernel → Restart & Run All** (equivalent to running top-to-bottom).

---

## ⚠️ Notes when you run them

1. **Take them in order `1_1 → 1_4`** — 1_2 assumes you know what an agent is,
   1_3 assumes you've seen tools, 1_4 reuses the checkpointer from 1_3.
2. **Copy `.env.example` to `.env`** (in `djef_chef/`) or paste the key in the
   setup cell / Colab Secrets. `.env` is git-ignored — keys never leave your machine.
3. **Lesson 1_4 needs `assets/`** — it sends `banner_dark_pink_contacts.png` and
   `liecio-calming-rain-257596.mp3` as image + audio content blocks. Keep the
   folder next to the notebook.
4. **Benign warnings** you can ignore: a LangSmith `403` (free key rejected by the
   tracing endpoint) and pydantic serializer warnings. Results are unaffected.
5. Notebooks **1_3** and **1_4** ship **with outputs** (0 error cells) so you can
   read the results without re-running. **1_1** and **1_2** ship without outputs —
   run **Run All Cells** to produce them.

---

## ➡️ What comes next

The four lessons feed directly into the module project:

| Lesson | Used by the project as |
| --- | --- |
| `1_1` | the Gemini model (`gemini-3.5-flash-lite`) |
| `1_2` | two tools — leftover matcher + Tavily web search |
| `1_3` | short-term memory (LangGraph + checkpointer) |
| `1_4` | structured messages (typed graph state) |

→ See **[`../djef_chef/README.md`](../djef_chef/README.md)** for the full DJEF
Chef app, its tests and its demo.

---

🇩🇿 **Mabrouk!** — **by Kassouar Fatima 🇩🇿** · Module 1 — Create Agent
