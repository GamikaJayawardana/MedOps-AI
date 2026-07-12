from langgraph.checkpoint.postgres import PostgresSaver

from app.config import settings
from app.agents.graph_state import MedOpsState
from app.agents.graph import (
    triage_node,
    route_after_triage,
    resource_node,
    shift_node,
    regulatory_node,
)
from langgraph.graph import StateGraph, START, END

import os

# Explicitly allow our own Pydantic models to be deserialized from checkpoints.
os.environ.setdefault(
    "LANGGRAPH_ALLOWED_MSGPACK_MODULES",
    "app.schemas.telemetry,app.schemas.shift,app.schemas.compliance",
)


def build_checkpointed_graph(checkpointer):
    """Same graph as before, but with a checkpointer attached."""
    graph = StateGraph(MedOpsState)

    graph.add_node("triage", triage_node)
    graph.add_node("resource", resource_node)
    graph.add_node("shift", shift_node)
    graph.add_node("regulatory", regulatory_node)

    graph.add_edge(START, "triage")
    graph.add_conditional_edges(
        "triage",
        route_after_triage,
        {"continue": "resource", "stop": END},
    )
    graph.add_edge("resource", "shift")
    graph.add_edge("shift", "regulatory")
    graph.add_edge("regulatory", END)

    # The ONLY difference from before: pass the checkpointer to compile().
    return graph.compile(checkpointer=checkpointer)