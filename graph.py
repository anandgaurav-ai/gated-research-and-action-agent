import sqlite3
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from config import SENSITIVE_TOOLS, DB_PATH
from state import AgentState
from nodes import agent_node, tools_node_safe, tools_node_sensitive

# ── Routing ────────────────────────────────────────────────────
def should_continue(state: AgentState) -> str:
    """Route to safe_tools, sensitive_tools, or END."""
    last_message = state["messages"][-1]

    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return END
    
    for tool_call in last_message.tool_calls:
        if tool_call["name"] in SENSITIVE_TOOLS:
            return "sensitive_tools"
        
    return "safe_tools"

# ── Graph builder ──────────────────────────────────────────────
def build_graph(checkpointer = None):
    builder = StateGraph(AgentState)

    # Nodes
    builder.add_node("agent", agent_node)
    builder.add_node("safe_tools", tools_node_safe)
    builder.add_node("sensitive_tools", tools_node_sensitive)

    # Edges
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue)
    builder.add_edge("safe_tools", "agent")
    builder.add_edge("sensitive_tools", "agent")

    return builder.compile(
        checkpointer = checkpointer,
        interrupt_before = ["sensitive_tools"]
    )

# ── Database connection ────────────────────────────────────────
conn = sqlite3.connect(DB_PATH, check_same_thread = False)
checkpointer = SqliteSaver(conn)
graph = build_graph(checkpointer = checkpointer)