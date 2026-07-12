import json
import re

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
from groq import BadRequestError

from app.agents.llm import get_llm
from app.agents.tools import (
    check_equipment_inventory,
    find_transfer_ward,
    search_procedures,
)


SYSTEM_PROMPT = """You are a Resource Allocation Agent in a hospital control centre.
Given a description of a resource shortage, determine what equipment or overflow
capacity is needed.

Consult official hospital procedures and check real equipment availability using
the tools available to you before concluding. Cite any procedure codes you rely on.

Once you have the facts, give a brief recommendation (2-3 sentences) on how to
allocate resources."""


TOOLS = [check_equipment_inventory, find_transfer_ward, search_procedures]


def _parse_failed_call(error_str: str):
    """Extract a tool name and args from Groq's malformed 'failed_generation'.

    Groq sometimes returns e.g. <function=search_procedures{"query": "..."}</function>
    We rescue that instead of crashing.
    """
    match = re.search(r"<function=(\w+)\s*(\{.*?\})\s*</function>", error_str)
    if not match:
        return None
    name = match.group(1)
    try:
        args = json.loads(match.group(2))
    except json.JSONDecodeError:
        return None
    return name, args


def resource_agent(situation: str) -> str:
    """Run the Resource Agent on a described situation, return its recommendation."""
    llm = get_llm(temperature=0.0)
    llm_with_tools = llm.bind_tools(TOOLS)

    tools_by_name = {t.name: t for t in TOOLS}

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=situation),
    ]

    while True:
        try:
            ai_message = llm_with_tools.invoke(messages)
        except BadRequestError as e:
            # The model produced a malformed tool call. Rescue it.
            parsed = _parse_failed_call(str(e))
            if parsed is None:
                raise
            name, args = parsed
            print(f"  [rescued call] {name}({args})")
            tool_fn = tools_by_name.get(name)
            if tool_fn is None:
                raise
            result = tool_fn.invoke(args)
            print(f"  [tool result] {str(result)[:100]}")
            # Feed the rescued result back as if the tool had been called.
            messages.append(AIMessage(content=f"I will consult {name}."))
            messages.append(HumanMessage(content=f"Result of {name}: {result}"))
            continue

        messages.append(ai_message)

        if not ai_message.tool_calls:
            return str(ai_message.content)

        for call in ai_message.tool_calls:
            print(f"  [tool call] {call['name']}({call['args']})")
            tool_fn = tools_by_name[call["name"]]
            result = tool_fn.invoke(call["args"])
            print(f"  [tool result] {str(result)[:100]}")
            messages.append(
                ToolMessage(content=str(result), tool_call_id=call["id"])
            )