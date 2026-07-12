import uuid

from langgraph.checkpoint.postgres import PostgresSaver

from app.config import settings
from app.services.simulator import HospitalSimulator
from app.agents.graph_checkpointed import build_checkpointed_graph

# Open a checkpointer backed by Postgres.
with PostgresSaver.from_conn_string(settings.database_url) as checkpointer:
    # First time only: create the tables the checkpointer needs.
    checkpointer.setup()

    graph = build_checkpointed_graph(checkpointer)

    # Build a busy snapshot.
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
    }

    # A unique id for THIS run.
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print(f"=== RUNNING GRAPH (thread {thread_id[:8]}...) ===\n")
    final_state = graph.invoke(initial_state, config=config)

    print(f"\nRisk: {final_state['risk_level']}")
    if final_state["shift_plan"]:
        print(f"Plan: {final_state['shift_plan'].summary}")
        print(f"Compliance: {final_state['compliance_verdict'].status}")

    # Now prove state was SAVED: load it back from the database.
    print("\n=== LOADING SAVED STATE FROM POSTGRES ===")
    saved = graph.get_state(config)
    print(f"Saved state exists: {saved is not None}")
    print(f"Saved risk level: {saved.values.get('risk_level')}")
    print(f"Next node to run: {saved.next}")   # empty tuple = finished