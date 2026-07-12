from langgraph.graph import StateGraph, START, END

from app.agents.graph_state import MedOpsState
from app.agents.graph import (
    triage_node,
    route_after_triage,
    resource_node,
    shift_node,
    regulatory_node,
)


def commit_node(state: MedOpsState) -> dict:
    """The action a human must approve before it runs.
    In a real system this would apply the staff changes. Here we mark it done."""
    verdict = state["compliance_verdict"]
    if verdict and verdict.status == "approved":
        print("[commit] Shift changes COMMITTED after human approval.")
        return {"committed": True}
    print("[commit] Not committed (plan was not approved).")
    return {"committed": False}


def build_hitl_graph(checkpointer):
    """Graph that pauses before committing, awaiting human approval."""
    graph = StateGraph(MedOpsState)

    graph.add_node("triage", triage_node)
    graph.add_node("resource", resource_node)
    graph.add_node("shift", shift_node)
    graph.add_node("regulatory", regulatory_node)
    graph.add_node("commit", commit_node)

    graph.add_edge(START, "triage")
    graph.add_conditional_edges(
        "triage",
        route_after_triage,
        {"continue": "resource", "stop": END},
    )
    graph.add_edge("resource", "shift")
    graph.add_edge("shift", "regulatory")
    graph.add_edge("regulatory", "commit")
    graph.add_edge("commit", END)

    # THE KEY LINE: pause BEFORE 'commit' runs, awaiting human approval.
    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["commit"],
    )