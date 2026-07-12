from langgraph.graph import StateGraph, START, END

from app.agents.graph_state import MedOpsState
from app.agents.triage import triage_agent, format_telemetry
from app.agents.resource import resource_agent
from app.agents.shift import shift_optimiser
from app.agents.regulatory import regulatory_supervisor


# --- NODE 1: Triage ---
def triage_node(state: MedOpsState) -> dict:
    snapshot = state["snapshot"]
    assessment = triage_agent(snapshot)

    # Derive a simple risk level from the assessment text.
    text = assessment.upper()
    if "HIGH" in text:
        risk = "HIGH"
    elif "MODERATE" in text:
        risk = "MODERATE"
    else:
        risk = "LOW"

    print(f"[triage] risk={risk}")
    return {"triage_assessment": assessment, "risk_level": risk}


# --- ROUTER: conditional edge after triage ---
def route_after_triage(state: MedOpsState) -> str:
    """If risk is HIGH, continue to resource planning; otherwise stop."""
    return "continue" if state["risk_level"] == "HIGH" else "stop"


# --- NODE 2: Resource ---
def resource_node(state: MedOpsState) -> dict:
    snapshot = state["snapshot"]
    situation = format_telemetry(snapshot)
    recommendation = resource_agent(situation)
    print("[resource] recommendation produced")
    return {"resource_recommendation": recommendation}


# --- NODE 3: Shift Optimiser ---
def shift_node(state: MedOpsState) -> dict:
    snapshot = state["snapshot"]
    situation = format_telemetry(snapshot)
    plan = shift_optimiser(situation)
    print(f"[shift] {len(plan.changes)} changes proposed")
    return {"shift_plan": plan}


# --- NODE 4: Regulatory ---
def regulatory_node(state: MedOpsState) -> dict:
    plan = state["shift_plan"]
    if plan is None:
        raise ValueError("regulatory_node reached without a shift_plan")
    current_staff = state["current_staff"]
    verdict = regulatory_supervisor(plan, current_staff)
    print(f"[regulatory] verdict={verdict.status}")
    return {"compliance_verdict": verdict}


# --- BUILD THE GRAPH ---
def build_medops_graph():
    graph = StateGraph(MedOpsState)

    graph.add_node("triage", triage_node)
    graph.add_node("resource", resource_node)
    graph.add_node("shift", shift_node)
    graph.add_node("regulatory", regulatory_node)

    graph.add_edge(START, "triage")

    # Conditional: after triage, continue only if risk is HIGH.
    graph.add_conditional_edges(
        "triage",
        route_after_triage,
        {
            "continue": "resource",
            "stop": END,
        },
    )

    # The rest run in sequence.
    graph.add_edge("resource", "shift")
    graph.add_edge("shift", "regulatory")
    graph.add_edge("regulatory", END)

    return graph.compile()