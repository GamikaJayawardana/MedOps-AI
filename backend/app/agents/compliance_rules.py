from app.schemas.shift import ShiftPlan

# Deterministic safety constraints — these are absolute.
MIN_STAFF_PER_WARD = 8
MAX_SINGLE_MOVE = 10   # can't move more than 10 staff in one change

# Current staffing must be supplied so we can check the *result* of the plan.
def check_hard_rules(plan: ShiftPlan, current_staff: dict[str, int]) -> list[str]:
    """Return a list of violation strings. Empty list = all rules passed."""
    violations: list[str] = []

    # Simulate applying the plan to current staffing.
    projected = dict(current_staff)  # copy so we don't mutate the original
    for change in plan.changes:
        delta = change.staff_delta if change.action == "add" else -change.staff_delta
        projected[change.ward] = projected.get(change.ward, 0) + delta

        # Rule: no single move may exceed the cap.
        if change.staff_delta > MAX_SINGLE_MOVE:
            violations.append(
                f"{change.ward}: move of {change.staff_delta} exceeds max "
                f"single move of {MAX_SINGLE_MOVE}."
            )

    # Rule: no ward may end below the minimum safe staffing.
    for ward, count in projected.items():
        if count < MIN_STAFF_PER_WARD:
            violations.append(
                f"{ward}: projected staff {count} is below safe minimum "
                f"of {MIN_STAFF_PER_WARD}."
            )

    return violations