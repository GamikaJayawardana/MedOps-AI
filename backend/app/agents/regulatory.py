from typing import cast

from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.llm import get_llm
from app.agents.compliance_rules import check_hard_rules
from app.schemas.shift import ShiftPlan
from app.schemas.compliance import ComplianceVerdict


SYSTEM_PROMPT = """You are a Regulatory Supervisor Agent in a hospital control centre.
You review proposed staff reallocation plans for safety and sensibility.

The plan has ALREADY passed automated hard-rule checks (minimum staffing, move
limits). Your job is the softer judgment: is this plan sensible, efficient, and
free of obvious problems a rule might have missed?

Respond with a compliance verdict."""


def regulatory_supervisor(
    plan: ShiftPlan,
    current_staff: dict[str, int],
) -> ComplianceVerdict:
    """Validate a plan: hard rules first, then LLM judgment."""

    # --- Stage 1: deterministic hard rules ---
    violations = check_hard_rules(plan, current_staff)
    if violations:
        # Hard rule broken -> automatic rejection, no LLM needed.
        return ComplianceVerdict(
            status="rejected",
            violations=violations,
            reasoning="Plan violates one or more hard safety rules.",
        )

    # --- Stage 2: LLM judgment (only reached if hard rules passed) ---
    llm = get_llm(temperature=0.0)
    structured_llm = llm.with_structured_output(ComplianceVerdict)

    plan_description = f"Summary: {plan.summary}\nChanges:\n" + "\n".join(
        f"- {c.action} {c.staff_delta} staff at {c.ward} ({c.reason})"
        for c in plan.changes
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=plan_description),
    ]

    verdict = structured_llm.invoke(messages)
    return cast(ComplianceVerdict, verdict)