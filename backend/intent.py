import json
from backend.llm import ask_llm

def extract_intent(user_prompt: str) -> dict:
    system_prompt = f"""
Convert the user request into JSON.
Only return JSON.

Fields:
goal, schedule, api, notification, ai_usage, style

User request:
{user_prompt}
"""
    response = ask_llm(system_prompt)
    return json.loads(response)
