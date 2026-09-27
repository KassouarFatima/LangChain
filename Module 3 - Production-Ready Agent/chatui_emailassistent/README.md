# DJEF Email Assistant

**Djazair Email Facilitator** — A professional Algerian-themed email assistant with Human-in-the-Loop approval, dynamic tools, and Algerian cultural flair.

by Kassouar Fatima 🇩🇿 — Module 3 — Production-Ready Agent

---

## 📸 Screenshots

### 1 · Chat — authenticate, then the inbox comes back

Type `kassouarfatima@gmail.com, password123` → the agent authenticates and the
next message returns the inbox, rendered on the dark Algerian theme:

<img src="../screenshots/01_chat_inbox.png" width="760" alt="DJEF Email Assistant — chat returning the inbox on the dark theme">

*Left: demo-inbox status in the sidebar · Center: hero card with the 🇩🇿
attribution · Right: the agent's `📬 Your Inbox — Marhaba! 🇩🇿📬` reply with the
light text readable on the `#0b1120` background.*

> The full screenshot set lives in
> [`../screenshots/`](../screenshots). Captured on the fixed build — the main
> content area is dark (it previously rendered a **white** background under
> light text, which made the whole page look empty).

---

## What I added

| # | What | Where | Why |
|---|------|-------|-----|
| 1 | **Mail-mode dispatch** (`auto` / `real` / `simulated`), `MailConfig.usable`, `_DEMO_PASSWORDS`, mtime re-read of `.env` | `email_agent_service.py` | Fixed the `b'Empty username or password.'` IMAP crash — the socket is never opened without a real password |
| 2 | **`runner.mail_status()`** + **`components.mail_mode_status()`**, rendered *inside* `sidebar_auth()` | `runner.py`, `components.py` | Shows live in the sidebar which mail mode is active and how to go live |
| 3 | **`.env` / `.env.example` mail block** | app root | Documents `MAIL_MODE`, `EMAIL_PASSWORD`, `EMAIL_ADDRESS` |
| 4 | **`design.theme_css()` rewritten to `st.markdown()`** | `design.py` | The old version cached an `st.empty()` in a module-level global; after the first rerun that delta path went stale and the `<style>` **silently never reached the DOM** → light text on a white page. This was the "text doesn't show" bug |
| 5 | **`streamlit/.streamlit/config.toml`** (dark theme + `fileWatcherType = "none"`) | new file | It must sit next to the launched folder — the older copy one level up was never read. Also stops an external `app.py` save from aborting a chat run mid-reply |
| 6 | **`--server.fileWatcherType none`** on the launcher | `run_app.cmd` | Same reason, at the CLI so it survives even if the config file is moved |
| 7 | **Removed `— بيكي خير`** from the hero subtitle | `design.py` | Per spec |
| 8 | **`3.5_email_agent.ipynb`** — 37 cells, executed top-to-bottom, 0 error cells | `streamlit/` | The lab version of this app, shipped with its outputs |
| 9 | **Sidebar status is inside `sidebar_auth()`** | `components.py` | Keeps it intact even when `app.py` is rewritten externally |

---

## Features

- **Algerian green/gold theme** with 🇩🇿 branding
- **Two mail modes** — built-in demo inbox by default, real Gmail once you add an App Password (*see [Mail modes](#mail-modes--and-the-fix-for-the-imap-error)*)
- **Human-in-the-Loop** approval on send_email (approve / edit / reject)
- **Dynamic tools** — only authenticate before auth, all tools after
- **Dynamic prompt** — doorman vs email assistant
- **Dark mode** with CSS-only theming
- **Algerian phrases** — "Marhaba!", "Khoya!", "Mabrouk!", "Barak Allahu fik!"

---

## Setup Steps

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get a Gemini API key
- Go to https://aistudio.google.com/app/apikey
- Copy your API key

### 3. Configure `.env`
Rename `.env.example` to `.env` and fill in:
```env
GOOGLE_API_KEY="your-gemini-api-key-here"
GEMINI_API_KEY="your-gemini-api-key-here"
```

### 4. Run the app
Double-click `run_app.cmd` or:
```bash
streamlit run streamlit/app.py --server.port 8518
```

### 5. Authenticate
- Enter your email and password in the sidebar
- Default: `kassouarfatima@gmail.com` / `password123`

---

## Mail modes — and the fix for the IMAP error

An earlier build of this app called Gmail unconditionally:

```python
from_pw = os.getenv("EMAIL_PASSWORD", "")   # "" when the key is missing
mail.login(from_addr, from_pw)              # blank password
```

so any run without an `EMAIL_PASSWORD` came back with:

```
❌ IMAP error! 🇩🇿
Saha, something went wrong: b'Empty username or password. 5b1f17b1804b1-49ff9072710mb594939845e9'.
```

**The app now never opens a socket unless the password is a real one.** Settings
are read from the nearest `.env`, an empty value counts as *unset*, and empty /
placeholder passwords (`password123`, `changeme`, …) are rejected up front.

| `MAIL_MODE` | Behaviour |
|---|---|
| `auto` *(default)* | Real Gmail when `EMAIL_PASSWORD` holds an App Password, otherwise the built-in demo inbox |
| `real` | Always attempt the network; failures name the exact `.env` key instead of leaking the raw server reply |
| `simulated` | Never touch the network |

The current status is shown live in the **sidebar**:

- 📧 **Real mail** — credentials are usable, SMTP/IMAP will be used
- 📬 **Demo inbox** — the built-in store, with the reason and how to go live
- 📉 **Real mail requested** — `MAIL_MODE=real` but the credential is missing

`.env` is re-read whenever the file changes, so pasting an App Password and
re-running the app is enough — no restart of the interpreter needed.

**To send real Gmail:** turn on 2-Step Verification, then create a 16-character
App Password at <https://myaccount.google.com/apppasswords> and put it in
`EMAIL_PASSWORD`.

---

## The notebook

`streamlit/3.5_email_agent.ipynb` is the **lab version of this app** — same
tools, same middleware, same HITL decisions, no widgets. It runs top-to-bottom:

1. imports + `load_dotenv()`
2. `EmailContext` / `AuthenticatedState`
3. the in-memory store **and the mail-mode fix above**
4. `authenticate` · `check_inbox` · `send_email`
5. `dynamic_tool_call` (the door) and `dynamic_prompt` (the voice)
6. `create_agent(...)` with `InMemorySaver` and `HumanInTheLoopMiddleware`
7. authenticate → check inbox → send (interrupts) → **approve**
8. **reject** example and **edit** example
9. `pprint(response)` and *Mabrouk! 🇩🇿*

> Cells use **top-level `await`** rather than `asyncio.run(...)` — a Jupyter
> kernel already runs an event loop. `runner.py` keeps `asyncio.run()` because
> it runs outside one.

```bash
cd streamlit
jupyter lab 3.5_email_agent.ipynb     # Kernel -> Restart & Run All
```

---

## Usage

| Action | Example |
|--------|---------|
| Authenticate | `kassouarfatima@gmail.com, password123` |
| Check inbox | `check my inbox` |
| Send email | `send an email to someone@example.com saying hello` |
| Show all emails | Click 📬 in sidebar |
| Theme | Dark mode only — `#0b6b4f` / `#064c39` / `#d49a32` / `#fbf8f0` / `#dcefe6` / `#17352a` |

---

## 🧭 How it works — worked examples

### Example 1 · Authenticate (dynamic tools + dynamic prompt)

```
you  →  kassouarfatima@gmail.com, password123
agent →  Marhaba! Successfully authenticated! Welcome to DJEF. ✉️🇩🇿
```

**What happens under the hood**

1. `dynamic_prompt` sees you are *not* authenticated → returns the **doorman**
   system prompt: ask for credentials, do nothing else.
2. `dynamic_tool_call` sees you are *not* authenticated → exposes **only**
   `authenticate`. `check_inbox` and `send_email` are not even attached.
3. The model calls `authenticate(addr, pwd)` → `AuthenticatedState.ok = True`.

### Example 2 · Check the inbox (tool switch)

```
you  →  check my inbox
agent →  📬 Your Inbox — Marhaba! 🇩🇿📬
         📥 [2026-09-27 20:49:00] boss@example.com  Subject: Project deadline
         ...
```

**What happens under the hood**

1. `dynamic_prompt` → the **DJEF email assistant** prompt (Algerian voice).
2. `dynamic_tool_call` → now **all three** tools: `authenticate`, `check_inbox`,
   `send_email`.
3. `check_inbox()` reads the store — the built-in demo inbox by default, real
   Gmail once `MAIL_MODE` resolves to real mail (see [Mail modes](#mail-modes--and-the-fix-for-the-imap-error)).

### Example 3 · Send an email → **Human-in-the-Loop interrupt**

```
you  →  send an email to someone@example.com saying hello
agent →  ⏸️ Pending draft:
         To: someone@example.com
         Subject: Hello
         ...

         Approval needed — approve, edit, or reject.
         [✅ Approve]  [✏️ Edit]  [❌ Reject]
```

**What happens under the hood**

1. `HumanInTheLoopMiddleware` is configured on `send_email`, so the agent run
   **stops before** the tool executes and `runner.run` returns `__HITL__:<body>`.
2. `app.py` shows the pending draft plus the three buttons and sets
   `session_state["interrupted"] = True`.
3. Choose one:
   - **Approve** → the run resumes and the mail is delivered →
     `**Marhaba!** Your email has been sent successfully!`
   - **Edit** → the draft is rewritten, then sent.
   - **Reject** → the run resumes with a rejection; nothing is sent.

### Example 4 · State survives the conversation

`InMemorySaver.checkpointer` + `thread_id` keep the thread alive, so
`state_schema` (messages, interrupts) and `context_schema` (`EmailContext`,
`AuthenticatedState`) are both restored on every turn — you authenticate **once**
and stay authenticated for the rest of the session.

---

## 🖥️ Recommended demo sequence

1. `kassouarfatima@gmail.com, password123` → authenticate
2. `check my inbox` → inbox appears
3. `send an email to someone@example.com saying hello` → interrupt + 3 buttons
4. ✅ **Approve** → sent
5. `send an email ...` again, then ✏️ **Edit** the subject → sent
6. `send an email ...` again, then ❌ **Reject** → nothing sent
7. 📬 **Show all emails** → everything above, sent and received

---

## Project Structure

```
chatui_emailassistent/
├── run_app.cmd              # Launch script
├── requirements.txt         # Dependencies
├── README.md                # This file
├── .env.example             # Config template (incl. mail settings)
└── streamlit/
    ├── app.py               # Main app
    ├── runner.py            # Agent invocation + HITL
    ├── components.py        # UI widgets
    ├── design.py            # Theme + CSS
    ├── email_agent_service.py  # Agent + tools + mail transport
    ├── 3.5_email_agent.py   # Plain-Python version of the agent
    ├── 3.5_email_agent.ipynb   # Notebook version (lab)
    └── .env                 # Configuration
```

---

## Algerian Phrases Used

- **Marhaba!** — Hello!
- **Khoya** — Brother/friend (affectionate)
- **Saha** — Health/thank you (used in errors)
- **Mabrouk!** — Congratulations!
- **Barak Allahu fik!** — God bless you!
- **Yalla!** — Let's go!
- **Bienvenue!** — Welcome!
- **بيكي خير** — May you be well
