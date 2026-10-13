# Studio simulation — test the DJEF agent like Studio does

This folder is the second of the three entry points. It lets you **exercise the
exact same graph** that LangGraph Studio would render, directly in your
terminal — so you can verify the agent (tools, memory, model loop) before or
without opening the browser.

```
your question
   │
   ▼
model ──► tools (match_leftover_recipes / search_recipe_instructions) ──► model ──► answer
   │                                                                       ▲
   └────────────── MemorySaver (thread_id) saves state after every turn ────┘
```

## 1 · Run the terminal simulation

From the project root:

```bash
uv run python studio_simulation/simulate.py
```

Example session:

```
DJEF Chef · Studio simulation
thread: sim-1a2b3c4d   model: gemini-3.6-flash   tavily: on
you> I have chickpeas, tomatoes, onion, and cumin. What can I make?
DJEF> (checking your kitchen…)
      graph nodes: model → tools → model
      tool step: 'match_leftover_recipes({"ingredients": "chickpeas, tomatoes, onion, and cumin", ...})'
DJEF> Chickpea and vegetable tagine (طاجين الحمص) — ...

you> What did I say I had?           # memory check — no need to repeat
DJEF> You told me you have chickpeas, tomatoes, onion, and cumin.

you> /reset                          # new thread (new MemorySaver conversation)
```

Commands: `/reset` new isolated thread · `/quit` exit.

## 2 · Run the interactive Studio (browser version)

From the project root, in a terminal:

```bash
uv run langgraph dev
```

Then open the Studio URL the command prints. You will see only three nodes:
`__start__ → model → tools → __end__`. Submit a prompt and watch the tool
call, the observation, and the final answer light up on the canvas — identical
to what the simulation above prints as text.

## 3 · Example tests to try (same in simulate.py, Studio, or Streamlit)

| Prompt | Tool that should fire | Expected recommendation |
| --- | --- | --- |
| `I have chickpeas, tomatoes, onion, and cumin.` | `match_leftover_recipes` | Chickpea and vegetable tagine (100%) |
| `I have semolina.` | `match_leftover_recipes` | Mhadjeb (100%) |
| `I have lentils and tomatoes.` | `match_leftover_recipes` | Harira (100%) |
| `Make that vegan for four people.` | memory only (no tool needed) | Vegan-safe quantities, no animal products |
| `What did I say I was allergic to?` | memory only | Repeats the profile from onboarding |
| `How is chakhchoukha traditionally made?` | `search_recipe_instructions` | Steps + cited source URLs |

> The automated offline tests live in `tests/` (`uv run pytest`) — they never
> call Gemini or Tavily. The prompts above are the **online** checks.

---

**Author:** Kassouar Fatima — built from the LangChain notebooks `1_1`–`1_4`.
---

## ✍️ Author

**Fatima Kassouar** — AI Engineering Student · Designer · Web / Mobile Developer
`ML` · `DL` · `NLP` · `Agent` · `Chatbot` · `Computer Vision` · `Autonomous AI`

- 💼 LinkedIn: [linkedin.com/in/fatima-kassouar](https://linkedin.com/in/fatima-kassouar)
- 🐙 GitHub: [github.com/KassouarFatima](https://github.com/KassouarFatima)
- 📧 Email: [kassouarfatima20@gmail.com](mailto:kassouarfatima20@gmail.com)
