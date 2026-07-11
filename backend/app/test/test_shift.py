from app.agents.shift import shift_optimiser

situation = (
    "Respiratory ward: 100% full, 17 staff. Cardiology: 100% full, 12 staff. "
    "General ward: 70% full, 20 staff, 12 beds free. "
    "Pediatric: 100% full, 14 staff. "
    "The general ward has spare capacity and staff; the others are overwhelmed."
)

plan = shift_optimiser(situation)

print("=== SUMMARY ===")
print(plan.summary)
print("\n=== PROPOSED CHANGES ===")
for change in plan.changes:
    print(f"  {change.action.upper()} {change.staff_delta} staff "
          f"{'to' if change.action == 'add' else 'from'} {change.ward} "
          f"— {change.reason}")