from dotenv import load_dotenv
import os

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
VERIFIED_SENDER  = os.getenv("VERIFIED_SENDER")

# Sensitive tools
SENSITIVE_TOOLS = {"send_email", "save_note"}

# Database
DB_PATH = "gated_research_and_action_agent.db"

# Model
MODEL_NAME = "gpt-4o"

# System Prompt
SYSTEM_PROMPT = """You are a research assistant with the ability to search 
the web, do calculations, send emails, and save notes.

RULES:
- Always search before answering factual questions
- Never call a sensitive tool (send_email, save_note) in the same
step as a safe tool
- When sending emails or saving notes, be concise and professional
- If information is missing to complete a task, ask for it before calling a tool
"""