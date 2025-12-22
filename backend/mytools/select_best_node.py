import json
import re
from backend.llm_config import get_llm

SELECT_BEST_NODE_PROMPT = """
You are an n8n workflow architect.

Workflow Intent:
{final_intent}

Possible Nodes:
{possible_nodes}

Best Practice:
{documentation}

Selection Strategy:
- Identify the PRIMARY workflow action
- Select ONE node that directly performs that action
- Ignore helper and orchestration nodes

Rules:
- Return JSON only
- No explanations
- No markdown

Output format:
{{
  "best_node": "NODE_NAME",
  "confidence": 0.0,
  "reason": "short explanation"
}}
"""

def _extract_json(text: str) -> dict | None:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except Exception:
        return None


def select_best_node(final_intent: str, possible_nodes: list, bp_context: dict) -> dict:
    llm = get_llm()

    prompt = SELECT_BEST_NODE_PROMPT.format(
        final_intent=final_intent,
        possible_nodes=possible_nodes,
        documentation=bp_context["documentation"]
    )

    response = llm.invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)

    print("\n[DEBUG] Raw LLM output:\n", content)

    data = _extract_json(content)

    if data and "best_node" in data:
        return {
            "best_node": data.get("best_node"),
            "confidence": float(data.get("confidence", 0.0)),
            "reason": data.get("reason", "")
        }

    # ❌ Explicit error instead of silent fallback
    return {
        "best_node": None,
        "confidence": 0.0,
        "reason": "LLM failed to return a valid JSON response",
        "error": {
            "type": "LLM_OUTPUT_INVALID",
            "message": "Unable to extract a valid JSON object from LLM output"
        }
    }
