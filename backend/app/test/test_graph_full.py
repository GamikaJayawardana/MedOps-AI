from app.services.simulator import HospitalSimulator
from app.agents.graph import build_medops_graph

graph = build_medops_graph()
sim = HospitalSimulator()

# Tick several times to build up a busy hospital.
snapshot = sim.tick()
for _ in range(6):
    snapshot = sim.tick()

# Extract current staff per ward for the compliance checker.
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

print("=== RUNNING GRAPH ===\n")
final_state = graph.invoke(initial_state)

print("\n=== FINAL STATE ===")
print(f"Risk level: {final_state['risk_level']}")
print(f"Triage: {final_state['triage_assessment']}\n")

if final_state["shift_plan"] is None:
    print("Hospital calm — no action taken (graph stopped after triage).")
else:
    print(f"Resource: {final_state['resource_recommendation']}\n")
    print(f"Shift plan summary: {final_state['shift_plan'].summary}")
    verdict = final_state["compliance_verdict"]
    print(f"Compliance: {verdict.status} — {verdict.reasoning}")