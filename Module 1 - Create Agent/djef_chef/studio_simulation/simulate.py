"""Studio-style terminal simulation of the DJEF agent.

This is the "Simulation" of what LangGraph Studio shows you in the browser:
each turn prints every node the graph visits (``model``, ``tools``), the tool
calls the agent makes, and the final answer — with real in-memory memory
(``MemorySaver``) across turns.

Run it from the project root:

    uv run python studio_simulation/simulate.py             # one conversation
    uv run python studio_simulation/simulate.py --thread demo-1

Commands inside the chat: ``/reset`` (new thread), ``/quit``.

For the interactive graphical version of the exact same graph, use LangGraph
Studio instead (see README.md).
"""

from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from notebook.chef_service import (  # noqa: E402
    ConfigurationError,
    conversation_config,
    get_graph,
    service_status,
)

GREEN = "\033[92m"
GOLD = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def trace_turn(
    graph: Any,
    config: dict[str, Any],
    prompt: str,
) -> dict[str, Any]:
    """Run one user turn and record what Studio would show on its canvas.

    Returns the streamed answer plus the list of ``(node, tool_calls)`` steps.
    """
    nodes_entered: list[str] = []
    tool_steps: list[dict[str, Any]] = []
    answer_parts: list[str] = []

    for mode, payload in graph.stream(
        {"messages": [{"role": "user", "content": prompt}]},
        config=config,
        stream_mode=["updates", "messages"],
    ):
        if mode == "updates":
            for node, update in payload.items():
                if node in ("__start__", "__end__"):
                    continue
                nodes_entered.append(node)
                if node == "tools":
                    tool_steps.append(
                        {
                            "node": node,
                            "messages": [str(msg) for msg in (update or {}).get("messages", [])],
                        }
                    )
        else:  # mode == "messages": (chunk, metadata)
            chunk, _metadata = payload
            text = getattr(chunk, "text", None)
            if isinstance(text, str) and text:
                answer_parts.append(text)

    answer = "".join(answer_parts).strip()
    if not answer:
        try:  # Fall back to the saved state when the provider sent no text chunks.
            snapshot = graph.get_state(config)
            messages = (snapshot.values or {}).get("messages", [])
        except Exception:
            messages = []
        for message in reversed(messages):
            if message.__class__.__name__.startswith("AI"):
                content = getattr(message, "content", "")
                if isinstance(content, str):
                    answer = content
                break
    if not answer:
        raise RuntimeError("The model returned an empty response.")

    return {
        "answer": answer,
        "nodes_entered": nodes_entered,
        "tool_steps": tool_steps,
    }


def simulate_loop(*, thread_id: str | None = None) -> None:
    """Interactive terminal chat with the same graph that Streamlit and Studio use."""
    status = service_status()
    if not status["gemini_configured"]:
        raise ConfigurationError(
            "GEMINI_API_KEY is missing. Copy .env.example to .env, add the key, "
            "and run this command again from the project root."
        )

    graph = get_graph()
    thread = thread_id or f"sim-{uuid.uuid4().hex[:8]}"
    config = conversation_config(thread)

    print(f"{BOLD}{GREEN}DJEF Chef · Studio simulation{RESET}   {CYAN}by Kassouar Fatima{RESET}")
    print(
        f"{CYAN}thread:{RESET} {thread}   {CYAN}model:{RESET} {status['model']}   "
        f"{CYAN}tavily:{RESET} {'on' if status['tavily_configured'] else 'off'}"
    )
    print("Type your kitchen question, `/reset` for a new thread, or `/quit`.\n")

    while True:
        try:
            prompt = input(f"{BOLD}you> {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not prompt:
            continue
        if prompt == "/quit":
            break
        if prompt == "/reset":
            thread = f"sim-{uuid.uuid4().hex[:8]}"
            config = conversation_config(thread)
            print(f"{CYAN}New thread:{RESET} {thread}\n")
            continue

        print(f"{GOLD}DJEF> (checking your kitchen…){RESET}")
        try:
            trace = trace_turn(graph, config, prompt)
        except Exception as exc:  # Keep the simulation alive on API hiccups.
            print(f"{GOLD}DJEF> ⚠️  {type(exc).__name__}: {exc}{RESET}\n")
            continue

        names = " → ".join(dict.fromkeys(trace["nodes_entered"])) or "(no tool run)"
        print(f"{CYAN}      graph nodes: {BOLD}{names}{RESET}")
        for step in trace["tool_steps"]:
            preview = (step["messages"][0] if step["messages"] else "")[:180]
            print(f"{CYAN}      tool step: {BOLD}{preview}{RESET}")
        print(f"{GREEN}{BOLD}DJEF> {RESET}{trace['answer']}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="DJEF Chef Studio simulation")
    parser.add_argument("--thread", default=None, help="thread id (default: random)")
    args = parser.parse_args()
    simulate_loop(thread_id=args.thread)


if __name__ == "__main__":
    main()
