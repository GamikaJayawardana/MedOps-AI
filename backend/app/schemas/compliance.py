from pydantic import BaseModel, Field
from typing import Literal


class ComplianceVerdict(BaseModel):
    status: Literal["approved", "rejected", "needs_review"] = Field(
        description="Overall compliance decision for the proposed plan."
    )
    violations: list[str] = Field(
        default_factory=list,
        description="Specific rule violations found (empty if none).",
    )
    reasoning: str = Field(
        description="Brief explanation of the verdict."
    )