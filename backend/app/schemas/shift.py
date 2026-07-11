from pydantic import BaseModel, Field
from typing import Literal

# Schema for representing a change in staff allocation for a specific ward.
class StaffChange(BaseModel):
    # The ward where the staff change is to be applied.
    ward: str = Field(description="The ward this change applies to.")
    action: Literal["add", "remove"] = Field(
        description="Whether to add or remove staff from this ward."
    )
    staff_delta: int = Field(
        description="How many staff members to add or remove (positive number)."
    )
    reason: str = Field(description="Brief reason for this change.")

# Schema for representing a proposed shift plan, which includes multiple staff changes and a summary.
class ShiftPlan(BaseModel):
    # The list of proposed staff changes across wards.
    changes: list[StaffChange] = Field(
        description="The list of proposed staff changes across wards."
    )
    summary: str = Field(
        description="One-sentence summary of the overall rebalancing strategy."
    )