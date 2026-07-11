from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

from app.agents.llm import get_llm
from app.agents.tools import check_equipment_inventory, find_transfer_ward


SYSTEM_PROMPT = """You are a Resource Allocation Agent in a hospital control centre.
Given a description of a resource shortage, determine what equipment or overflow
capacity is needed, and use the available tools to check real availability.

Use tools to gather facts before concluding. Once you have the facts, give a brief
recommendation (2-3 sentences) on how to allocate resources."""


TOOLS = [check_equipment_inventory, find_transfer_ward]


def resource_agent(situation: str) -> str:
    """Run the Resource Agent on a described situation, return its recommendation."""
    llm = get_llm(temperature=0.0)
    llm_with_tools = llm.bind_tools(TOOLS)

    # A lookup so we can run a tool by the name the model gives us.
    tools_by_name = {t.name: t for t in TOOLS}

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=situation),
    ]

    # The tool-calling loop: keep going until the model stops asking for tools.
    while True:
        ai_message = llm_with_tools.invoke(messages)
        messages.append(ai_message)

        # If the model didn't request any tools, it's done — return its answer.
        if not ai_message.tool_calls:
            return str(ai_message.content)

        # Otherwise, run each requested tool and feed results back.
        for call in ai_message.tool_calls:
            print(f"  [tool call] {call['name']}({call['args']})")
            tool_fn = tools_by_name[call["name"]]
            result = tool_fn.invoke(call["args"])
            print(f"  [tool result] {result}")
            messages.append(
                ToolMessage(content=str(result), tool_call_id=call["id"])
            )