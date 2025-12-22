# backend/mytools/generate_possible_nodes.py

import json
from backend.llm_config import get_llm

GENERATE_NODES_PROMPT = """
You are an expert n8n workflow architect.

User Intent:
{{intent}}

Task:
Generate ONLY the n8n nodes REQUIRED to implement this intent.

CRITICAL RULES:
- Nodes must be directly related to the intent topic
- DO NOT invent nodes
- Platform names are NOT nodes
- If no native node exists, use "HTTP Request"
- Avoid unrelated domains entirely

Allowed node examples:
- HTTP Request
- AI Agent
- Set
- Merge
- IF
- Chat Trigger
- Respond to Chat

Output requirements:
- Return ONLY valid JSON
- Output a JSON array of node names
- No explanations
- No empty strings
"""

def generate_possible_nodes(intent: str, bp_context: dict) -> list:
    llm = get_llm()

    prompt = GENERATE_NODES_PROMPT.format(intent=intent)
    response = llm.invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)

    try:
        nodes = json.loads(content)
        return [
            n for n in nodes
            if isinstance(n, str) and n.strip()
        ]
    except Exception:
        return []
