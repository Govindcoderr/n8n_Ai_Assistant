import json
import re
from backend.llm_config import get_llm

# ==========================================================
# EMBEDDED NODE REGISTRY (VALIDATION ONLY — NOT GENERATION)
# ==========================================================

N8N_NODES = {
    "http request": "HTTP Request",
    "ai agent": "AI Agent",
    "set": "Set",
    "merge": "Merge",
    "if": "IF",
    "cron": "Cron",
    "chat trigger": "Chat Trigger",
    "respond to chat": "Respond to Chat",
}

def normalize_node_name(name: str):
    if not isinstance(name, str):
        return None
    return N8N_NODES.get(name.strip().lower())


# ==========================================================
# GENERIC BEST PRACTICE (NO DOMAIN POLLUTION)
# ==========================================================

def dummy_best_practice():
    """
    BEST PRACTICE: API-Driven Automation

    Principles:
    - User intent defines the domain
    - Nodes must be directly related to the intent
    - Do NOT invent nodes
    - If no native node exists, the workflow is invalid

    Techniques:
    - REST API integration
    - OAuth / token authentication
    - Data transformation
    - Error handling & retries
    """
    return {
        "toolName": "Generic Automation Best Practice",
        "displayTitle": "API Automation",
        "tool": lambda: dummy_best_practice
    }


# ==========================================================
# LLM: GENERATE POSSIBLE NODES
# ==========================================================

GENERATE_NODES_PROMPT = """
You are an expert n8n workflow architect.

User Intent:
{intent}

Task:
Generate ONLY the n8n nodes REQUIRED to implement this intent.

CRITICAL RULES:
- Nodes MUST be real n8n nodes
- Platform names (e.g. PowerBI) are NOT nodes
- Do NOT invent nodes
- Avoid unrelated domains entirely
- If no valid node exists, return an EMPTY array

Allowed examples:
- HTTP Request
- AI Agent
- Set
- Merge
- IF
- Cron
- Chat Trigger
- Respond to Chat

Output:
- JSON array ONLY
- No explanations
- No empty strings
"""

def generate_possible_nodes(intent: str) -> list:
    llm = get_llm()

    prompt = GENERATE_NODES_PROMPT.format(intent=intent)
    response = llm.invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)

    try:
        nodes = json.loads(content)
        nodes = [
            n for n in nodes
            if isinstance(n, str) and n.strip()
        ]
    except Exception:
        print("[ERROR] Invalid node list from LLM:\n", content)
        return []

    # ✅ STRICT VALIDATION: remove invalid nodes
    valid_nodes = []
    for n in nodes:
        normalized = normalize_node_name(n)
        if normalized:
            valid_nodes.append(normalized)

    # Remove duplicates while preserving order
    return list(dict.fromkeys(valid_nodes))


# ==========================================================
# LLM: SELECT BEST NODE (STRICT — NO FALLBACK)
# ==========================================================

SELECT_BEST_NODE_PROMPT = """
You are an expert n8n workflow architect.

User Intent:
{intent}

Candidate Nodes:
{nodes}

Task:
Select the SINGLE most important node.

RULES:
- Node MUST exist in n8n
- Platform names are NOT nodes
- Choose the primary execution node
- If no valid node exists, return an invalid node name

Return ONLY valid JSON:
{{
  "best_node": "NODE_NAME",
  "confidence": 0.0,
  "reason": "short explanation"
}}
"""

def _extract_json(text: str):
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except Exception:
        return None

def select_best_node(intent: str, nodes: list) -> dict:
    llm = get_llm()

    prompt = SELECT_BEST_NODE_PROMPT.format(
        intent=intent,
        nodes=nodes
    )

    response = llm.invoke(prompt)
    content = response.content if hasattr(response, "content") else str(response)

    print("\n[DEBUG] Raw LLM output:\n", content)

    data = _extract_json(content)

    if not data or "best_node" not in data:
        return {
            "best_node": None,
            "confidence": 0.0,
            "reason": "LLM failed to return valid JSON",
            "error": {
                "type": "LLM_OUTPUT_INVALID",
                "message": "No valid JSON object could be extracted"
            }
        }

    raw_node = data["best_node"]
    normalized = normalize_node_name(raw_node)

    # ❌ STRICT MODE — NO FALLBACK
    if not normalized:
        return {
            "best_node": None,
            "confidence": 0.0,
            "reason": f"Invalid n8n node returned by LLM: {raw_node}",
            "error": {
                "type": "INVALID_NODE",
                "message": (
                    "The LLM returned a conceptual or non-existent n8n node. "
                    "No fallback is applied."
                )
            }
        }

    return {
        "best_node": normalized,
        "confidence": float(data.get("confidence", 0.0)),
        "reason": data.get("reason", "")
    }


# ==========================================================
# PIPELINE ORCHESTRATOR
# ==========================================================

def generate_best_node(intent: str) -> dict:
    _ = dummy_best_practice()  # reserved for future use

    possible_nodes = generate_possible_nodes(intent)
    best_node = select_best_node(intent, possible_nodes)

    return {
        "possible_nodes": possible_nodes,
        **best_node
    }


# ==========================================================
# LOCAL TEST
# ==========================================================

if __name__ == "__main__":
    result = generate_best_node(
        "Create a workflow that automatically send message through whatsapp"
    )
    print(result)
