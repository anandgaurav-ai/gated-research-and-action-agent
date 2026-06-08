from datetime import datetime
from langchain_core.messages import HumanMessage, ToolMessage
from graph import graph

# ── Audit log ─────────────────────────────────────────────────
audit_log = []

def log_action(thread_id: str, tool_name:str, args: dict, approved: bool):
    """Record every approval/rejection."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "thread_id": thread_id,
        "tool": tool_name,
        "args": args,
        "approved": approved
    }
    audit_log.append(entry)
    status = "✅ APPROVED" if approved else "❌ REJECTED"
    print(f" [{status}] {tool_name} | {entry['timestamp'][:19]}")


# ── State repair ───────────────────────────────────────────────
def repair_state(config: dict):
     """Fix incomplete state — append rejection ToolMessages."""
     state = graph.get_state(config)
     last = state.values["messages"][-1]

     if hasattr(last, "tool_calls") and last.tool_calls:
          patches = [
               ToolMessage(
                    content = f"rejected by Human. '{tc['name']}' was not executed.",
                    tool_call_id = tc["id"]
               )
               for tc in last.tool_calls
          ]
          graph.update_state(config, {"messages": patches})
          print("State Repaired")


# ── Main run function ──────────────────────────────────────────

def run_with_approval(user_input: str, thread_id: str = "default"):
    config = {"configurable": {"thread_id": thread_id}}
    print(f"\n{'='*55}")
    print(f"User: {user_input}")
    print(f"{'='*55}")

    # Step 1 - invoke graph
    graph.invoke(
        {"messages": [HumanMessage(content=user_input)]},
          config = config
    )
     

    # Step 2 — check if paused
    current_state = graph.get_state(config)
    
    if current_state.next:
     
        print(f"\n Paused at: {current_state.next}")
        last_message = current_state.values["messages"][-1]

        # Step 3 — show pending tool calls
        if last_message.tool_calls:
            print("\n Pending actions: ")
            for tc in last_message.tool_calls:
                print(f" Tool: {tc['name']}")
                print(f" Args: {tc['args']}")
          
        # Get approval      
        approval = input("\nApprove? (yes/no): ").strip().lower()

        if approval == 'yes':
            # Log each tool call as approved
            for tc in last_message.tool_calls:
                log_action(thread_id, tc["name"], tc["args"], approved = True)

            # Resume Graph
            print("\n Resuming...")
            result = graph.invoke(None, config = config)
            reply = result["messages"][-1].content
            print(f"\nAssistant: {reply}")
            return reply
        else:
            # Log each tool call as rejected
            for tc in last_message.tool_calls:
                log_action(thread_id, tc["name"], tc["args"], approved=False)

            # Repair state so next call on this thread works cleanly
            repair_state(config)
            print("\n❌ Action rejected. State cleaned up.")
            return "Action cancelled."
        
    else:
        # Graph finished without interrupt
        reply = current_state.values["messages"][-1].content
        print(f"\nAssistant: {reply}")
        return reply
    


# ── Print audit log ────────────────────────────────────────────
def print_audit_log():
    print(f"\n{'='*55}")
    print("AUDIT LOG")
    print(f"{'='*55}")
    if not audit_log:
        print("No actions recorded yet.")
        return
    for entry in audit_log:
        status = "Approved" if entry["approved"] else "Rejected"
        print(f"{status} [{entry['timestamp'][:19]}] "
              f"{entry['tool']} | thread: {entry['thread_id']}")
        print(f"   args: {entry['args']}")