from langchain_core.messages import SystemMessage, HumanMessage
from typing import cast
from app.agents.llm import get_llm
from app.schemas.shift import ShiftPlan


SYSTEM_PROMPT = """You are a Shift Optimiser Agent in a hospital control centre.
Given the current staffing situation across wards, propose a set of staff
reallocation changes to balance load against demand.

Rules:
- Only move staff between wards; do not invent new staff out of nowhere.
- Prioritise wards that are at or near full occupancy.
- Keep the plan realistic and minimal."""


def shift_optimiser(situation: str) -> ShiftPlan:
    """Run the Shift Optimiser, returning a validated ShiftPlan object."""
    llm = get_llm(temperature=0.0)
    structured_llm = llm.with_structured_output(ShiftPlan)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=situation),
    ]

    plan = structured_llm.invoke(messages)
    return cast(ShiftPlan, plan)