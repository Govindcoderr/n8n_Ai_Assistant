import json
from backend.llm_config import get_llm

GENERATE_NODES_PROMPT = """
You are an n8n workflow expert.

Workflow Intent:
{final_intent}

Best Practice:
{documentation}

Task:
Based strictly on the best practice above, list ALL n8n nodes
that could reasonably be used.

Rules (VERY IMPORTANT):
- Return ONLY valid JSON
- Do NOT add explanations
- Do NOT add markdown
- Do NOT add text before or after JSON
- Output must be a JSON array of strings
- Use real n8n node names

Example output:
["Chat Trigger", "YouTube Get a Video", "AI Agent"]
"""

def generate_possible_nodes(final_intent: str, bp_context: dict) -> list:
    llm = get_llm()

    prompt = GENERATE_NODES_PROMPT.format(
        final_intent=final_intent,
        documentation=bp_context["documentation"]
    )

    response = llm.invoke(prompt)

    # ✅ FIX 1: Extract content correctly
    content = response.content if hasattr(response, "content") else response

    try:
        nodes = json.loads(content)

        if isinstance(nodes, list):
            # remove duplicates while preserving order
            return list(dict.fromkeys(nodes))

    except Exception as e:
        print("Failed to parse node list:", content)

    return []
