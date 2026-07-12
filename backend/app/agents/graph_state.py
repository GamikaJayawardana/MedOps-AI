from typing import TypedDict, Optional

from app.schemas.telemetry import Telemetry
from app.schemas.shift import ShiftPlan
from app.schemas.compliance import ComplianceVerdict


class MedOpsState(TypedDict):
    # --- Input ---
    snapshot: Telemetry              # the hospital reading we're reasoning about
    current_staff: dict[str, int]    # ward -> staff count, for rule checking

    # --- Filled in by agents as the graph runs ---
    triage_assessment: str
    risk_level: str                  # "LOW" / "MODERATE" / "HIGH"
    resource_recommendation: str
    shift_plan: Optional[ShiftPlan]
    compliance_verdict: Optional[ComplianceVerdict]