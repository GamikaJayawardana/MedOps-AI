import uuid

from langgraph.checkpoint.postgres import PostgresSaver

from app.config import settings
from app.schemas.telemetry import Telemetry
from app.agents.graph_hitl import build_hitl_graph


def _initial_state(snapshot: Telemetry) -> dict:
    current_staff = {w.ward: w.staff_on_shift for w in snapshot.wards}
    return {
        "snapshot": snapshot,
        "current_staff": current_staff,
        "triage_assessment": "",
        "risk_level": "",
        "resource_recommendation": "",
        "shift_plan": None,
        "compliance_verdict": None,
        "committed": False,
    }


def run_analysis(snapshot: Telemetry) -> dict:
    """Run the agent graph until it pauses before commit.
    Returns a summary dict for the frontend, plus the thread_id to resume with."""
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    with PostgresSaver.from_conn_string(settings.database_url) as checkpointer:
        checkpointer.setup()
        graph = build_hitl_graph(checkpointer)

        # Run until it pauses (interrupt_before commit) or ends early (low risk).
        graph.invoke(_initial_state(snapshot), config=config)
        state = graph.get_state(config)

    return _summarise(state, thread_id)


def resume_analysis(thread_id: str) -> dict:
    """Resume a paused graph after human approval."""
    config = {"configurable": {"thread_id": thread_id}}

    with PostgresSaver.from_conn_string(settings.database_url) as checkpointer:
        graph = build_hitl_graph(checkpointer)
        graph.invoke(None, config=config)   # None = resume from checkpoint
        state = graph.get_state(config)

    return _summarise(state, thread_id)


def _summarise(state, thread_id: str) -> dict:
    """Turn the graph state into a plain dict the frontend can render."""
    values = state.values
    plan = values.get("shift_plan")
    verdict = values.get("compliance_verdict")

    return {
        "thread_id": thread_id,
        "risk_level": values.get("risk_level", ""),
        "triage_assessment": values.get("triage_assessment", ""),
        "resource_recommendation": values.get("resource_recommendation", ""),
        "awaiting_approval": bool(state.next),   # True if paused before commit
        "committed": values.get("committed", False),
        "plan": None if plan is None else {
            "summary": plan.summary,
            "changes": [
                {
                    "ward": c.ward,
                    "action": c.action,
                    "staff_delta": c.staff_delta,
                    "reason": c.reason,
                }
                for c in plan.changes
            ],
        },
        "compliance": None if verdict is None else {
            "status": verdict.status,
            "violations": verdict.violations,
            "reasoning": verdict.reasoning,
        },
    }