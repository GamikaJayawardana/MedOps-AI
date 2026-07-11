from app.schemas.shift import ShiftPlan, StaffChange
from app.agents.regulatory import regulatory_supervisor

current_staff = {
    "respiratory": 17,
    "cardiology": 12,
    "general": 20,
    "pediatric": 14,
}

# --- Case A: a reasonable plan (should pass hard rules, reach LLM) ---
good_plan = ShiftPlan(
    summary="Rebalance staff from general to overwhelmed wards.",
    changes=[
        StaffChange(ward="general", action="remove", staff_delta=6, reason="spare capacity"),
        StaffChange(ward="respiratory", action="add", staff_delta=3, reason="full"),
        StaffChange(ward="cardiology", action="add", staff_delta=3, reason="full"),
    ],
)

# --- Case B: an unsafe plan (strips general below minimum) ---
bad_plan = ShiftPlan(
    summary="Aggressively strip general ward.",
    changes=[
        StaffChange(ward="general", action="remove", staff_delta=15, reason="move everyone"),
        StaffChange(ward="respiratory", action="add", staff_delta=15, reason="all here"),
    ],
)

for label, plan in [("GOOD PLAN", good_plan), ("BAD PLAN", bad_plan)]:
    print(f"=== {label} ===")
    verdict = regulatory_supervisor(plan, current_staff)
    print(f"  status: {verdict.status}")
    print(f"  violations: {verdict.violations}")
    print(f"  reasoning: {verdict.reasoning}")
    print()