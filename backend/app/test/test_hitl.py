import uuid

from langgraph.checkpoint.postgres import PostgresSaver

from app.config import settings
from app.services.simulator import HospitalSimulator
from app.agents.graph_hitl import build_hitl_graph

with PostgresSaver.from_conn_string(settings.database_url) as checkpointer:
    checkpointer.setup()
    graph = build_hitl_graph(checkpointer)

    sim = HospitalSimulator()
    snapshot = sim.tick()
    for _ in range(6):
        snapshot = sim.tick()
    current_staff = {w.ward: w.staff_on_shift for w in snapshot.wards}

    initial_state = {
        "snapshot": snapshot,
        "current_staff": current_staff,
        "triage_assessment": "",
        "risk_level": "",
        "resource_recommendation": "",
        "shift_plan": None,
        "compliance_verdict": None,
        "committed": False,
    }

    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    # --- RUN 1: runs until it PAUSES before commit ---
    print("=== RUN 1: running until pause ===\n")
    graph.invoke(initial_state, config=config)

    # Check where it stopped.
    state = graph.get_state(config)
    print(f"\n--- PAUSED ---")  # noqa: F541
    print(f"Next node waiting to run: {state.next}")   # should be ('commit',)
    if state.values.get("shift_plan"):
        print(f"Proposed plan: {state.values['shift_plan'].summary}")
        print(f"Compliance: {state.values['compliance_verdict'].status}")
    print(f"Committed yet? {state.values.get('committed')}")   # False

    # --- HUMAN APPROVES (simulated) ---
    print("\n>>> Human reviews the plan and clicks APPROVE <<<\n")

    # --- RUN 2: resume from the pause by invoking with None ---
    print("=== RUN 2: resuming after approval ===\n")
    graph.invoke(None, config=config)   # None = continue from checkpoint

    final = graph.get_state(config)
    print(f"\n--- FINISHED ---")  # noqa: F541
    print(f"Next node: {final.next}")           # empty = done
    print(f"Committed? {final.values.get('committed')}")   # True