from app.services.simulator import HospitalSimulator
from app.services.analysis import run_analysis, resume_analysis

sim = HospitalSimulator()
snapshot = sim.tick()
for _ in range(6):
    snapshot = sim.tick()

print("=== RUNNING ANALYSIS ===")
result = run_analysis(snapshot)
print(f"Risk: {result['risk_level']}")
print(f"Awaiting approval: {result['awaiting_approval']}")
if result["plan"]:
    print(f"Plan: {result['plan']['summary']}")
    print(f"Compliance: {result['compliance']['status']}")

if result["awaiting_approval"]:
    print("\n=== APPROVING ===")
    final = resume_analysis(result["thread_id"])
    print(f"Committed: {final['committed']}")