"""Tests for the Studio-style terminal simulation (studio_simulation/)."""

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel

from notebook.chef_service import build_chef_graph, conversation_config
from studio_simulation.simulate import trace_turn


def test_trace_turn_reports_nodes_and_answer() -> None:
    model = GenericFakeChatModel(messages=iter(("A vegan tagine for four.",)))
    graph = build_chef_graph(model=model, tools=[])

    trace = trace_turn(graph, conversation_config("sim-test"), "make it vegan")

    assert trace["answer"] == "A vegan tagine for four."
    assert "model" in trace["nodes_entered"]
    assert isinstance(trace["tool_steps"], list)
