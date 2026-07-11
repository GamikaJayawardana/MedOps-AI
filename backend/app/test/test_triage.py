from app.services.simulator import HospitalSimulator
from app.agents.triage import triage_agent

sim = HospitalSimulator()

# Tick a few times so the hospital fills up to something interesting.
snapshot = sim.tick()
for _ in range(5):
    snapshot = sim.tick()

print("=== SNAPSHOT ===")
print(f"pressure: {snapshot.hospital_pressure}")
for w in snapshot.wards:
    print(f"  {w.ward}: {w.occupancy_rate:.0%} full, {w.available_beds} beds")

print("\n=== TRIAGE ASSESSMENT ===")
print(triage_agent(snapshot))