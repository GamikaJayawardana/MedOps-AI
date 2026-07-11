from langgraph.graph import StateGraph, START, END
from app.agents.state import HospitalState

# Define the nodes in the graph
def classify_node(state: HospitalState) -> dict:
    pressure = state["pressure"]
    if pressure < 0.4:
        label = "calm"
    elif pressure < 0.75:
        label = "busy"
    else:
        label = "critical"
    print(f"[classify] pressur={pressure} -> {label}")
    return {"classification": label}


def calm_node(state: HospitalState) -> dict:
    return {"action": "No action needed. Routine monitoring."}

def busy_node(state: HospitalState) -> dict:
    return {"action": "Alert charge nurse. Prepare overflow beds."}

def critical_node(state: HospitalState) -> dict:
    return {"action": "ESCALATE: activate surge protocol, page on-call staff."}

def route_by_classification(state: HospitalState) -> str:
    # This function determines the next node in the graph based on the classification of the hospital state.
    return state["classification"] 

def build_graph():
    graph = StateGraph(HospitalState)

    # Register nodes: give each a name and its function.
    graph.add_node("classify", classify_node)
    graph.add_node("calm", calm_node)
    graph.add_node("busy", busy_node)
    graph.add_node("critical", critical_node)

    # Fixed edge: start -> classify (always).
    graph.add_edge(START, "classify")

    # Conditional edge: after classify, the router decides where to go.
    graph.add_conditional_edges(
        "classify",
        route_by_classification,
        {
            "calm": "calm",
            "busy": "busy",
            "critical": "critical",
        },
    )

    # Fixed edges: each action node -> END.
    graph.add_edge("calm", END)
    graph.add_edge("busy", END)
    graph.add_edge("critical", END)

    return graph.compile()