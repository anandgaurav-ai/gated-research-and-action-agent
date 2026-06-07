import os
from datetime import datetime
from langchain_core.tools import tool
from config import SENDGRID_API_KEY, VERIFIED_SENDER

# -------Safe tools------------------------------------------------

@tool
def web_search(query: str) -> str:
    """Search the web for current information about a topic.
    Use for any factual question or recent news.
    Do NOT use for math calculations."""

    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results = 3))
        if not results:
            return "No results found."
        return "\n".join(
            f"{r['title']}: {r['body']}"
            for r in results
        )
    except Exception as e:
        return f"Search failed: {e}"
    

@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression.
    Use for any arithmetic or numeric calculation.
    E.g. '1234 * 5678' or '15 / 100 * 4750'.
    Do NOT use for factual lookups."""

    try:
        import math
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        allowed.update({"abs": abs, "round": round})
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"Result: {result}"
    except Exception as e:
        return f"Calculator Error: {e}"
    

# ---------Sensitive tools ----------------------------

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a recipient.
    Use ONLY when explicitly asked to send an email.
    Requires: recipient address, subject line, body text."""
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        message = Mail(
            from_email=VERIFIED_SENDER,
            to_emails=to,
            subject=subject,
            plain_text_content=body
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return f"Email sent successfully. Status: {response.status_code}"
    except Exception as e:
        return f"Email failed: {e}"
    

@tool
def save_note(title: str, content: str) -> str:
    """Save a note to a local file.
    Use when asked to save, record, or store information for later.
    Requires: title and content."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open("notes.txt", "a") as f:
            f.write(f"\n[{timestamp}] {title}\n{content}\n{'-'*40}\n")
        return f"Note '{title}' saved successfully."
    except Exception as e:
        return f"Save failed: {e}"
    

# ── Tool registry ──────────────────────────────────────────────
tools = [web_search, calculator, send_email, save_note]
TOOL_MAP = {t.name: t for t in tools}