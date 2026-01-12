# backend/mytools/langchain_tools.py

from langchain_core.tools import tool
from typing import List, Dict
from backend.mytools.registry_node_generator import (
    generate_workflow_nodes_from_registry,
    format_workflow_nodes_for_api
)
from backend.mytools.generate_from_parsed_bp import (
    generate_workflow_from_parsed_bp,
    workflow_to_n8n_format
)
from backend.mytools.find_best_practice_tool import create_get_best_practices_tool

@tool
def get_registry_nodes(prompt: str, technique: str = "auto") -> List[Dict]:
    """
    Generate n8n nodes using the deterministic registry-based system.
    
    Args:
        prompt: User workflow description
        technique: Node selection technique (auto, hybrid, scoring, direct, category)
    
    Returns:
        List of formatted node dictionaries
    """
    raw_nodes = generate_workflow_nodes_from_registry(
        user_intent=prompt,
        technique=technique
    )
    return format_workflow_nodes_for_api(raw_nodes)


@tool
def get_best_practices(techniques: List[str]) -> str:
    """
    Retrieve best practices documentation for given techniques.
    
    Args:
        techniques: List of technique names (e.g., ["scheduling", "notification"])
    
    Returns:
        Formatted best practices text
    """
    tool_data = create_get_best_practices_tool()
    tool = tool_data["tool"]
    result = tool.invoke({"techniques": techniques})
    data = result.get("data")
    if isinstance(data, dict):
        return data.get("message", "")
    return data if isinstance(data, str) else ""


@tool
def generate_full_workflow(
    prompt: str,
    best_practices_text: str,
    techniques: List[str]
) -> Dict:
    """
    Generate complete workflow with nodes and connections.
    
    Args:
        prompt: Original user intent
        best_practices_text: Documentation from best practices
        techniques: List of detected techniques
    
    Returns:
        Full workflow with nodes, connections, and optional n8n JSON
    """
    workflow = generate_workflow_from_parsed_bp(
        user_intent=prompt,
        best_practices_text=best_practices_text,
        techniques=techniques
    )

    return {
        "description": getattr(workflow, "description", ""),
        "nodes": [
            {
                "id": n.id,
                "name": n.name,
                "type": n.type,
                "position": n.position,
                "parameters": n.parameters,
                "notes": getattr(n, "notes", "")
            }
            for n in workflow.nodes
        ],
        "connections": [
            {
                "source": c.source,
                "target": c.target,
                "sourceOutput": getattr(c, "source_output", "main"),
                "targetInput": getattr(c, "target_input", "main")
            }
            for c in workflow.connections
        ],
        "n8n_json": workflow_to_n8n_format(workflow)
    }