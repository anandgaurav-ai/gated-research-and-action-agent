from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, ToolMessage
from config import SENSITIVE_TOOLS, SYSTEM_PROMPT, MODEL_NAME
from state import AgentState
from tools import tools, TOOL_MAP

# ── LLM setup ──────────────────────────────────────────────────
llm = ChatOpenAI(model = MODEL_NAME)
llm_with_tools = llm.bind_tools(tools)

# ── Agent node ─────────────────────────────────────────────────
def agent_node(state: AgentState) -> dict:
    """LLM decides what to do next."""
    messages = SystemMessage(content = SYSTEM_PROMPT) + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# ── Safe tools node ────────────────────────────────────────────
def tools_node_safe(state:AgentState) -> dict:
    """Execute only safe tools. Skip sensitive ones."""
    last_message = state["messages"][-1]
    results = []

    for tool_call in last_message.tool_calls:
        if tool_call["name"] not in SENSITIVE_TOOLS:

            # Guard against hallucinated tool names
            if tool_call["name"] not in TOOL_MAP:
                results.append(ToolMessage(
                    content = f"Error: tool '{tool_call['name']}' not found.",
                    tool_call_id = tool_call["id"]
                ))
                continue

            tool_fn = TOOL_MAP[tool_call["name"]]
            result = tool_fn.invoke(tool_call["args"])
            result = result if result is not None else "Tool returned no output."
            results.append(ToolMessage(
                content = str(result),
                tool_call_id = tool_call["id"]
            ))
    return {"messages": results}


# ── Sensitive tools node ───────────────────────────────────────
def tools_node_sensitive(state: AgentState) -> dict:
    """Execute sensitive tools. Append placeholder for safe ones."""
    last_message = state["messages"][-1]
    results = []

    for tool_call in last_message.tool_calls:
        if tool_call["name"] in SENSITIVE_TOOLS:
            # Guard against hallucinated tool names
            if tool_call["name"] not in TOOL_MAP:
                results.append(ToolMessage(
                    content = f"Error: 'tool {tool_call['name']}' not found.",
                    tool_call_id = tool_call["id"]
                ))
                continue

            tool_fn = TOOL_MAP[tool_call["name"]]
            result = tool_fn.invoke(tool_call["args"])
            result = result if result is not None else "Tool returned no output."
            results.append(ToolMessage(
                content = str(result),
                tool_call_id = tool_call["id"]
            ))

        else:
            # Placeholder for safe tools — handled in safe_tools node
            results.append(ToolMessage(
                content = "Deferred to safe tool node.",
                tool_call_id = tool_call["id"]
            ))

    return {"messages": results}