# Gated Research & Action Agent

A production-style LangGraph agent with human-in-the-loop approval
for sensitive actions.

## Features
- Web search and calculator run freely (no approval needed)
- Email and note saving require human approval before execution
- Full conversation persistence via SQLite checkpointing
- State repair on rejection — no broken threads
- Audit log for every approved/rejected action

## Architecture
- `safe_tools` node — runs calculator, web_search autonomously
- `sensitive_tools` node — runs send_email, save_note with interrupt
- `SqliteSaver` — persists conversation state across sessions
- `graph.update_state()` — repairs state on human rejection

## Stack
LangGraph · LangChain · OpenAI GPT-4o · SQLite · SendGrid · DuckDuckGo

## Setup
pip install -r requirements.txt
cp .env.example .env  # add your API keys
python main.py

## Project Structure
config.py   — API keys, constants, system prompt
state.py    — AgentState definition
tools.py    — web_search, calculator, send_email, save_note
nodes.py    — agent, safe_tools, sensitive_tools nodes
graph.py    — graph builder, routing, checkpointing
runner.py   — run_with_approval, audit log, state repair
main.py     — entry point, test cases