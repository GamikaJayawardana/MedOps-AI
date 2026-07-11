from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.llm import get_llm
from app.schemas.telemetry import Telemetry


SYSTEM_PROMPT = """You are a Triage Analytics Agent in a hospital control centre.
Your job is to analyse real-time emergency department telemetry and predict
resource bottlenecks before they happen.

Be concise and clinical. Base your assessment ONLY on the data provided.
Respond in 2-3 short sentences: state the risk level (LOW / MODERATE / HIGH),
which ward(s) are most at risk, and the single most important reason."""


def format_telemetry(snapshot: Telemetry) -> str:
    """Turn the snapshot object into readable text for the LLM."""
    lines = [f"Overall hospital pressure: {snapshot.hospital_pressure:.2f} (0-1 scale)"]
    for w in snapshot.wards:
        lines.append(
            f"- {w.ward}: {w.patient_influx} arriving, "
            f"{w.available_beds} beds free, "
            f"{w.staff_on_shift} staff, "
            f"{w.occupancy_rate:.0%} full"
        )
    return "\n".join(lines)


def triage_agent(snapshot: Telemetry) -> str:
    """Run the Triage Agent on one snapshot, return its assessment text."""
    llm = get_llm(temperature=0.0)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=format_telemetry(snapshot)),
    ]

    response = llm.invoke(messages)
    return str(response.content)