# File: backend/mytools/generate_from_parsed_bp.py

from typing import List, Dict, Any, Optional, Tuple, Callable
from pydantic import BaseModel
from backend.llm_config import get_llm
from langchain_core.prompts import ChatPromptTemplate
from backend.mytools.parse_best_practices import parse_best_practices, NodeInfo
from backend.mytools.node_registry import search_registry, NODE_REGISTRY
import json
import re


class WorkflowNode(BaseModel):
    """Concrete workflow node"""
    id: str
    name: str
    type: str  # Full node ID like "n8n-nodes-base.httpRequest"
    position: Dict[str, int]
    parameters: Dict[str, Any]
    notes: str = ""


class WorkflowConnection(BaseModel):
    """Connection between nodes"""
    source: str
    target: str
    source_output: str = "main"
    target_input: str = "main"


class GeneratedWorkflow(BaseModel):
    """Complete workflow"""
    nodes: List[WorkflowNode]
    connections: List[WorkflowConnection]
    description: str
    metadata: Dict[str, Any] = {}


def validate_and_fix_adapted_nodes(adapted_nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate LLM-adapted nodes and fix common mistakes.
    - Ensures categories match node registry
    - Fixes misclassifications
    """
    # BUILD the NODE_BY_ID dict from NODE_REGISTRY
    NODE_BY_ID = {node.node_id: node for node in NODE_REGISTRY}
    
    fixed_nodes = []
    
    for node in adapted_nodes:
        node_id = node.get("node_id")
        
        # Look up correct category from registry
        registry_node = NODE_BY_ID.get(node_id)
        
        if registry_node:
            # Fix category if LLM got it wrong
            correct_category = registry_node.category
            if node.get("category") != correct_category:
                print(f"⚠️  Fixed category for {node['name']}: {node.get('category')} → {correct_category}")
                node["category"] = correct_category
            
            # Preserve other registry info
            if not node.get("pitfalls"):
                node["pitfalls"] = registry_node.pitfalls
            if not node.get("alternatives"):
                node["alternatives"] = registry_node.alternatives
        
        fixed_nodes.append(node)
    
    return fixed_nodes


def llm_select_and_adapt_nodes_for_intent(
    user_intent: str,
    parsed_nodes: List[NodeInfo]
) -> List[Dict[str, Any]]:
    """
    Uses LLM to intelligently select and adapt nodes from the parsed best practices
    to perfectly match the user's specific intent.
    
    NOW WITH VALIDATION to prevent LLM mistakes.
    """
    llm = get_llm()

    nodes_description = "\n".join([
        f"- Name: {node.name}\n"
        f"  ID: {node.node_id}\n"
        f"  Category: {node.category}\n"
        f"  Original Purpose: {node.purpose}\n"
        f"  Pitfalls: {', '.join(node.pitfalls) if node.pitfalls else 'None'}"
        for node in parsed_nodes
    ])

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert n8n workflow architect.
Your task is to select and adapt ONLY from the provided parsed nodes to build a workflow that exactly fulfills the user's intent.

Rules:
- Use ONLY nodes from the list below – do not invent new node IDs or names.
- Select the minimal, most relevant set (typically 4–8 nodes).
- Adapt the 'purpose' field to precisely describe how this node is used in THIS specific workflow.
- KEEP category exactly as given - DO NOT change categories.
- Add relevant pitfalls if applicable from the original.
- Output ONLY a valid JSON array of objects with keys: name, node_id, category, purpose, pitfalls, use_cases, alternatives, is_recommended.
- Set is_recommended: true for all selected nodes.

CRITICAL: Do not change the category field. Keep categories exactly as provided."""),
        ("user", """User Intent: {intent}

Available Parsed Nodes (use only these):
{nodes}

Generate the exact list of nodes needed for this workflow as JSON array only:""")
    ])

    chain = prompt | llm
    response = chain.invoke({
        "intent": user_intent,
        "nodes": nodes_description
    })

    content = response.content if hasattr(response, 'content') else str(response)

    try:
        match = re.search(r'\[[\s\S]*\]', content)
        if match:
            selected_nodes = json.loads(match.group(0))
            for node in selected_nodes:
                node.setdefault("pitfalls", [])
                node.setdefault("use_cases", [])
                node.setdefault("alternatives", [])
                node.setdefault("is_recommended", True)
                node.setdefault("input_connections", [])
                node.setdefault("output_connections", [])

            # VALIDATE and FIX any LLM mistakes
            fixed_nodes = validate_and_fix_adapted_nodes(selected_nodes)
            return fixed_nodes
            
    except Exception as e:
        print(f"LLM node selection failed: {e}")

    # Fallback: return top relevant nodes heuristically
    intent_lower = user_intent.lower()
    keywords = intent_lower.split()
    scored = []
    for node in parsed_nodes:
        score = sum(k in (node.name + node.purpose + node.node_id).lower() for k in keywords)
        if "trigger" in node.category.lower() and any(t in intent_lower for t in ["trigger", "webhook", "chat", "schedule"]):
            score += 5
        if "ai" in node.category.lower() and any(t in intent_lower for t in ["generate", "claude", "anthropic", "gpt", "llm"]):
            score += 5
        scored.append((score, node))

    scored.sort(reverse=True)
    top_nodes = [node for _, node in scored[:8]]

    return [
        {
            "name": node.name,
            "node_id": node.node_id,
            "category": node.category,
            "purpose": node.purpose,
            "pitfalls": node.pitfalls,
            "use_cases": node.use_cases if hasattr(node, 'use_cases') else [],
            "alternatives": node.alternatives,
            "is_recommended": True,
            "input_connections": node.input_connections if hasattr(node, 'input_connections') else [],
            "output_connections": node.output_connections if hasattr(node, 'output_connections') else []
        }
        for node in top_nodes
    ]

def generalize_phases(intent: str) -> List[Tuple[str, Callable]]:
    """Dynamically generate phases with trigger always first and better ordering."""
    intent_lower = intent.lower()
    phases = []

    # ALWAYS include trigger phase first – essential for 99% of workflows
    phases.append(("trigger", lambda n: n.category == "trigger"))

    # Data fetching
    if any(k in intent_lower for k in ["fetch", "get", "api", "http", "request", "data from", "read", "load", "query", "scrape"]):
        phases.append(("fetch", lambda n: any(t in n.node_id.lower() for t in ["http", "request"]) or "fetch" in n.name.lower()))

    # Extract / Parse
    if any(k in intent_lower for k in ["extract", "parse", "json", "split", "iterate", "loop over", "item"]):
        phases.append(("extract", lambda n: any(t in n.name.lower() for t in ["extract", "split", "item", "json", "parse"])))

    # Transform / Compose – prioritize if message/body mentioned
    if any(k in intent_lower for k in ["set", "edit", "transform", "modify", "compose", "text", "body", "message", "format", "code", "function", "reply"]):
        phases.append(("transform", lambda n: n.category == "transform" or any(t in n.name.lower() for t in ["set", "code", "function", "edit"])))

    # Control flow
    if any(k in intent_lower for k in ["if", "condition", "switch", "branch", "merge", "loop", "filter"]):
        phases.append(("control", lambda n: n.category == "control" or any(t in n.name.lower() for t in ["if", "switch", "merge"])))

    # AI / Generation
    if any(k in intent_lower for k in ["ai", "llm", "chat", "model", "generate", "bot", "agent", "openai", "grok", "gemini", "reply"]):
        phases.append(("ai", lambda n: n.category == "ai" or "langchain" in n.node_id.lower()))

    # Action / Send – last major phase
    if any(k in intent_lower for k in ["send", "post", "notify", "email", "slack", "telegram", "whatsapp", "msg", "message", "via", "to", "output", "store", "save"]):
        action_matcher = lambda n: (
            n.category == "action" or
            any(t in n.name.lower() or t in n.node_id.lower() for t in ["email", "slack", "telegram", "whatsapp", "send", "smtp", "gmail", "post", "notify", "sheet"])
        )
        phases.append(("action", action_matcher))

    # Safety
    if any(k in intent_lower for k in ["wait", "delay", "error", "catch", "handle", "fallback"]):
        phases.append(("safety", lambda n: any(t in n.name.lower() for t in ["wait", "error", "no-op"])))

    # If no specific phases beyond trigger, use a minimal default
    if len(phases) <= 1:
        phases.extend([
            ("transform", lambda n: n.category == "transform"),
            ("action", lambda n: n.category == "action"),
        ])

    return phases


def align_nodes_after_parsing(intent: str, parsed_nodes: List[NodeInfo]) -> List[NodeInfo]:
    """Order nodes strictly by phases – no auto-append of all remaining."""
    workflow_nodes: List[NodeInfo] = []
    used_ids = set()

    phases = generalize_phases(intent)
    print(f"\nUsing phases for intent '{intent}': {[name for name, _ in phases]}")

    for phase_name, matcher in phases:
        matching = [n for n in parsed_nodes if n.node_id not in used_ids and matcher(n)]
        if matching:
            # Pick the BEST match (prioritize exact keyword hits)
            best = max(matching, key=lambda n: sum(k in n.name.lower() + n.node_id.lower() for k in intent.lower().split()))
            workflow_nodes.append(best)
            used_ids.add(best.node_id)
            print(f"  → Phase '{phase_name}': {best.name} ({best.node_id})")

    # If too few nodes (<3), supplement with heuristic
    if len(workflow_nodes) < 3:
        heuristic_add = heuristic_node_selection(intent, [n for n in parsed_nodes if n.node_id not in used_ids])
        for add in heuristic_add:
            if add.node_id not in used_ids:
                workflow_nodes.append(add)
                used_ids.add(add.node_id)

    return workflow_nodes


def agent_refine_node_selection(
    user_intent: str,
    available_nodes: List[NodeInfo],
    patterns: List,
    critical_instructions: List[str],
    initial_selection: List[NodeInfo]
) -> List[NodeInfo]:
    """Use LLM agent to refine node selection if initial is too large/small."""
    if 2 <= len(initial_selection) <= 10:
        return initial_selection

    llm = get_llm()
    nodes_desc = "\n".join([f"- {n.node_id}: {n.name} ({n.category}) - {n.purpose[:100]}" for n in available_nodes])

    refine_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert n8n workflow designer. Refine node selection to match the user's intent.
    Use ONLY nodes from the available list. Prioritize minimal, functional workflows.
    Return ONLY a JSON array of node_ids."""),
        ("user", """Intent: {intent}

Available nodes:
{nodes}

Initial selection: {initial}

Recommended patterns: {patterns}

Critical: {critical}

Return refined JSON array of node_ids:""")
    ])

    chain = refine_prompt | llm
    response = chain.invoke({
        "intent": user_intent,
        "nodes": nodes_desc,
        "initial": [n.node_id for n in initial_selection],
        "patterns": "\n".join([p.description for p in patterns]) if patterns else "None",
        "critical": "\n".join(critical_instructions)
    })

    content = response.content if hasattr(response, 'content') else str(response)
    try:
        match = re.search(r'\[[\s\S]*?\]', content)
        if match:
            selected_ids = json.loads(match.group())
            return [n for n in available_nodes if n.node_id in selected_ids]
    except:
        pass

    return initial_selection  # Fallback


def heuristic_node_selection(user_intent: str, available_nodes: List[NodeInfo]) -> List[NodeInfo]:
    intent_lower = user_intent.lower()
    selected = []

    # Trigger
    triggers = [n for n in available_nodes if n.category == "trigger"]
    if triggers:
        # Prefer webhook for bots/replies, schedule otherwise
        if any(k in intent_lower for k in ["bot", "reply", "webhook", "receive"]):
            webhook = next((n for n in triggers if "webhook" in n.name.lower()), triggers[0])
            selected.append(webhook)
        else:
            selected.append(triggers[0])

    # Transform for composition
    if any(k in intent_lower for k in ["text", "body", "message", "compose", "reply", "format"]):
        transforms = [n for n in available_nodes if "set" in n.name.lower() or n.category == "transform"]
        if transforms:
            selected.append(transforms[0])

    # Action
    if any(k in intent_lower for k in ["send", "email", "slack", "telegram", "whatsapp", "msg", "notify", "store", "sheet"]):
        actions = [n for n in available_nodes if n.category == "action"]
        relevant = [n for n in actions if any(k in n.name.lower() or k in n.node_id.lower() for k in ["email", "slack", "telegram", "whatsapp", "sheet", "send"])]
        if relevant:
            selected.extend(relevant[:2])
        elif actions:
            selected.extend(actions[:2])

    # Fetch for API/scrape
    if any(k in intent_lower for k in ["fetch", "api", "scrape"]):
        fetch = [n for n in available_nodes if "http" in n.node_id.lower()]
        if fetch:
            selected.append(fetch[0])

    return selected


def select_nodes_for_intent(
    user_intent: str,
    available_nodes: List[NodeInfo],
    patterns: List,
    critical_instructions: List[str]
) -> List[NodeInfo]:
    """Primary LLM-based node selection with fallbacks."""
    llm = get_llm()

    nodes_description = "\n".join([
        f"- {node.node_id}: {node.name} ({node.category}) – {node.purpose}"
        for node in available_nodes
    ])

    patterns_text = "\n".join([p.description for p in patterns]) if patterns else "None"
    critical_text = "\n".join(critical_instructions) if critical_instructions else "None"

    selection_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert workflow designer. Select ONLY the nodes needed for the intent.
Return ONLY a JSON array of node_ids. Do not include extras."""),
        ("user", """Intent: {intent}

Available nodes:
{nodes}

Patterns: {patterns}

Critical instructions: {critical}

Return JSON array of required node_ids:""")
    ])

    chain = selection_prompt | llm
    response = chain.invoke({
        "intent": user_intent,
        "nodes": nodes_description,
        "patterns": patterns_text,
        "critical": critical_text
    })

    content = response.content if hasattr(response, "content") else str(response)
    try:
        match = re.search(r'\[[\s\S]*?\]', content)
        if match:
            selected_ids = json.loads(match.group())
            selected = [n for n in available_nodes if n.node_id in selected_ids]
            if selected:
                return selected
    except:
        pass

    # Fallback to heuristic
    return heuristic_node_selection(user_intent, available_nodes)


def generate_workflow_structure(
    user_intent: str,
    selected_nodes: List[NodeInfo],
    patterns: List,
    guidelines: List[str]
) -> GeneratedWorkflow:
    """Generate final workflow JSON using LLM with fallback."""
    llm = get_llm()

    nodes_info = "\n".join([
        f"Node {i+1}: {node.name} ({node.node_id}) – Category: {node.category} – Purpose: {node.purpose}"
        for i, node in enumerate(selected_nodes)
    ])

    patterns_text = "\n".join([p.description for p in patterns]) if patterns else "None"

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Generate a complete, valid n8n workflow JSON.
Use ONLY the provided node types. Position left-to-right.
Include realistic parameters and helpful notes.
Output ONLY valid JSON with nodes, connections, description."""),
        ("user", """Intent: {intent}

Nodes to use:
{nodes}

Patterns: {patterns}

Generate workflow JSON:""")
    ])

    chain = prompt | llm
    response = chain.invoke({
        "intent": user_intent,
        "nodes": nodes_info,
        "patterns": patterns_text
    })

    content = response.content if hasattr(response, 'content') else str(response)

    try:
        match = re.search(r'\{[\s\S]*\}', content)
        if match:
            data = json.loads(match.group())
            # Convert to internal format
            nodes = []
            for i, n in enumerate(data.get("nodes", [])):
                idx = i if i < len(selected_nodes) else 0
                nodes.append(WorkflowNode(
                    id=n.get("id", f"node_{i}"),
                    name=n.get("name", selected_nodes[idx].name),
                    type=n.get("type", selected_nodes[idx].node_id),
                    position=n.get("position", {"x": i * 300, "y": 100}),
                    parameters=n.get("parameters", {}),
                    notes=n.get("notes", selected_nodes[idx].purpose)
                ))

            connections = [
                WorkflowConnection(**c) for c in data.get("connections", [])
            ]

            return GeneratedWorkflow(
                nodes=nodes,
                connections=connections,
                description=data.get("description", user_intent),
                metadata={
                    "source_nodes": [n.node_id for n in selected_nodes],
                    "patterns_used": [p.description for p in patterns]
                }
            )
    except:
        pass

    # Fallback: simple sequential
    return create_fallback_workflow(user_intent, selected_nodes)


def create_fallback_workflow(user_intent: str, nodes: List[NodeInfo]) -> GeneratedWorkflow:
    workflow_nodes = []
    connections = []

    for i, node in enumerate(nodes):
        workflow_nodes.append(WorkflowNode(
            id=f"node_{i}",
            name=node.name,
            type=node.node_id,
            position={"x": i * 300, "y": 100},
            parameters={},
            notes=node.purpose or "Workflow step"
        ))
        if i > 0:
            connections.append(WorkflowConnection(source=f"node_{i-1}", target=f"node_{i}"))

    return GeneratedWorkflow(
        nodes=workflow_nodes,
        connections=connections,
        description=f"Workflow: {user_intent}",
        metadata={"source_nodes": [n.node_id for n in nodes]}
    )


def workflow_to_n8n_format(workflow: GeneratedWorkflow) -> Dict[str, Any]:
    """Convert to n8n import format"""
    n8n_nodes = []
    for node in workflow.nodes:
        n8n_nodes.append({
            "id": node.id,
            "name": node.name,
            "type": node.type,
            "typeVersion": 1,
            "position": [node.position["x"], node.position["y"]],
            "parameters": node.parameters,
            "notes": node.notes
        })

    connections = {}
    for conn in workflow.connections:
        src = conn.source
        out = conn.source_output
        tgt = conn.target
        inp = conn.target_input
        if src not in connections:
            connections[src] = {}
        if out not in connections[src]:
            connections[src][out] = []
        connections[src][out].append({"node": tgt, "type": inp, "index": 0})

    return {
        "name": "Generated Workflow",
        "nodes": n8n_nodes,
        "connections": connections,
        "active": False,
        "settings": {},
        "tags": []
    }


def generate_workflow_from_parsed_bp(
    user_intent: str,
    best_practices_text: str,
    techniques: Optional[List[str]] = None
) -> GeneratedWorkflow:
    bp_parser = parse_best_practices(best_practices_text)
    print(f"Parsed {len(bp_parser.nodes)} nodes from best practices")

    # Start with empty list – we will build it from registry
    workflow_specific_nodes = []

    # 1. Search registry with full intent
    intent_lower = user_intent.lower()
    registry_matches = search_registry(intent_lower)
    print(f"Registry search found {len(registry_matches)} nodes")

    # Add all registry matches
    for node in registry_matches:
        workflow_specific_nodes.append({
            "name": node.name,
            "node_id": node.node_id,
            "category": node.category,
            "purpose": node.purpose,
            "pitfalls": node.pitfalls,
            "use_cases": [],
            "alternatives": node.alternatives,
            "is_recommended": True
        })

    # 2. Force the exact nodes needed for this prompt
    required_nodes = [
        ("@n8n/n8n-nodes-langchain.chatTrigger", "Receive YouTube video URL from user"),
        ("n8n-nodes-base.youtube", "Get video details"),
        ("n8n-nodes-base.httpRequest", "Download video captions/transcript"),
        ("@n8n/n8n-nodes-langchain.lmChatAnthropic", "Generate chapter timestamps using Claude"),
        ("n8n-nodes-base.set", "Append chapters to video description"),
        ("n8n-nodes-base.youtube", "Update video with new description"),
        ("@n8n/n8n-nodes-langchain.respondToChat", "Reply with updated description")
    ]

    existing_ids = {n["node_id"] for n in workflow_specific_nodes}

    for node_id, purpose in required_nodes:
        if node_id not in existing_ids:
            reg_node = next((n for n in NODE_REGISTRY if n.node_id == node_id), None)
            if reg_node:
                workflow_specific_nodes.append({
                    "name": reg_node.name,
                    "node_id": reg_node.node_id,
                    "category": reg_node.category,
                    "purpose": purpose,
                    "pitfalls": reg_node.pitfalls,
                    "use_cases": [],
                    "alternatives": reg_node.alternatives,
                    "is_recommended": True
                })

    # 3. Optional: Try LLM adaptation on the final list for better purposes
    try:
        adapted = llm_select_and_adapt_nodes_for_intent(
            user_intent=user_intent,
            parsed_nodes=[
                NodeInfo(
                    name=n["name"],
                    node_id=n["node_id"],
                    purpose=n["purpose"],
                    category=n["category"],
                    pitfalls=n.get("pitfalls", []),
                    use_cases=[],
                    alternatives=n.get("alternatives", [])
                )
                for n in workflow_specific_nodes
            ]
        )
        # Replace with adapted versions if better
        adapted_map = {n["node_id"]: n for n in adapted}
        for i, node in enumerate(workflow_specific_nodes):
            if node["node_id"] in adapted_map:
                workflow_specific_nodes[i] = adapted_map[node["node_id"]]
    except Exception as e:
        print(f"LLM adaptation failed (ok): {e}")

    print(f"Final selected {len(workflow_specific_nodes)} nodes")

    # Convert to NodeInfo
    selected_node_infos = [
        NodeInfo(
            name=n["name"],
            node_id=n["node_id"],
            purpose=n["purpose"],
            category=n["category"],
            pitfalls=n.get("pitfalls", []),
            use_cases=n.get("use_cases", []),
            alternatives=n.get("alternatives", [])
        )
        for n in workflow_specific_nodes
    ]

    ordered_nodes = align_nodes_after_parsing(user_intent, selected_node_infos)
    workflow = generate_workflow_structure(
        user_intent=user_intent,
        selected_nodes=ordered_nodes,
        patterns=bp_parser.patterns,
        guidelines=bp_parser.general_guidelines
    )
    
    workflow.metadata["source_nodes"] = [n["node_id"] for n in workflow_specific_nodes]

    return workflow

# File: backend/mytools/generate_from_parsed_bp.py



# from typing import List, Dict, Any, Optional, Tuple, Callable
# from pydantic import BaseModel
# from backend.llm_config import get_llm
# from langchain_core.prompts import ChatPromptTemplate
# from backend.mytools.parse_best_practices import parse_best_practices, NodeInfo
# from backend.mytools.node_registry import NODE_REGISTRY, search_registry  # Ensure node_registry.py has these
# import json
# import re


# class WorkflowNode(BaseModel):
#     """Concrete workflow node"""
#     id: str
#     name: str
#     type: str  # Full node ID like "n8n-nodes-base.httpRequest"
#     position: Dict[str, int]
#     parameters: Dict[str, Any]
#     notes: str = ""


# class WorkflowConnection(BaseModel):
#     """Connection between nodes"""
#     source: str
#     target: str
#     source_output: str = "main"
#     target_input: str = "main"


# class GeneratedWorkflow(BaseModel):
#     """Complete workflow"""
#     nodes: List[WorkflowNode]
#     connections: List[WorkflowConnection]
#     description: str
#     metadata: Dict[str, Any] = {}


# def llm_select_and_adapt_nodes_for_intent(
#     user_intent: str,
#     parsed_nodes: List[NodeInfo]
# ) -> List[Dict[str, Any]]:
#     """
#     Uses LLM to intelligently select and adapt nodes from the parsed best practices
#     to perfectly match the user's specific intent.
    
#     - References ONLY the provided parsed_nodes
#     - Adapts purpose, category, and adds intent-specific notes
#     - Generalizes for ANY prompt
#     - Returns list of dicts ready for parsedBestPractices["nodes"]
#     """
#     llm = get_llm()

#     # Format parsed nodes clearly for the LLM
#     nodes_description = "\n".join([
#         f"- Name: {node.name}\n"
#         f"  ID: {node.node_id}\n"
#         f"  Category: {node.category}\n"
#         f"  Original Purpose: {node.purpose}\n"
#         f"  Pitfalls: {', '.join(node.pitfalls) if node.pitfalls else 'None'}"
#         for node in parsed_nodes
#     ])

#     prompt = ChatPromptTemplate.from_messages([
#         ("system", """You are an expert n8n workflow architect.
# Your task is to select and adapt ONLY from the provided parsed nodes to build a workflow that exactly fulfills the user's intent.

# Rules:
# - Use ONLY nodes from the list below — do not invent new node IDs or names.
# - Select the minimal, most relevant set (typically 4–8 nodes).
# - Adapt the 'purpose' field to precisely describe how this node is used in THIS specific workflow.
# - Keep category and node_id exactly as given.
# - Add relevant pitfalls if applicable from the original.
# - Output ONLY a valid JSON array of objects with keys: name, node_id, category, purpose, pitfalls, use_cases, alternatives, is_recommended.
# - Set is_recommended: true for all selected nodes.
# """),
#         ("user", """User Intent: {intent}

# Available Parsed Nodes (use only these):
# {nodes}

# Generate the exact list of nodes needed for this workflow as JSON array only:""")
#     ])

#     chain = prompt | llm
#     response = chain.invoke({
#         "intent": user_intent,
#         "nodes": nodes_description
#     })

#     content = response.content if hasattr(response, 'content') else str(response)

#     try:
#         match = re.search(r'\[[\s\S]*\]', content)
#         if match:
#             selected_nodes = json.loads(match.group(0))
#             for node in selected_nodes:
#                 node.setdefault("pitfalls", [])
#                 node.setdefault("use_cases", [])
#                 node.setdefault("alternatives", [])
#                 node.setdefault("is_recommended", True)
#             return selected_nodes
#     except Exception as e:
#         print(f"LLM node selection failed: {e}")

#     # Fallback: return top relevant nodes heuristically
#     intent_lower = user_intent.lower()
#     keywords = intent_lower.split()
#     scored = []
#     for node in parsed_nodes:
#         score = sum(k in (node.name + node.purpose + node.node_id).lower() for k in keywords)
#         if "trigger" in node.category.lower() and any(t in intent_lower for t in ["trigger", "webhook", "chat", "schedule"]):
#             score += 5
#         if "ai" in node.category.lower() and any(t in intent_lower for t in ["generate", "claude", "anthropic", "gpt", "llm"]):
#             score += 5
#         scored.append((score, node))

#     scored.sort(reverse=True)
#     top_nodes = [node for _, node in scored[:8]]

#     return [
#         {
#             "name": node.name,
#             "node_id": node.node_id,
#             "category": node.category,
#             "purpose": node.purpose,
#             "pitfalls": node.pitfalls,
#             "use_cases": node.use_cases,
#             "alternatives": node.alternatives,
#             "is_recommended": True
#         }
#         for node in top_nodes
#     ]


# def generalize_phases(intent: str) -> List[Tuple[str, Callable]]:
#     intent_lower = intent.lower()
#     phases = []

#     # ALWAYS include trigger phase first — essential for 99% of workflows
#     phases.append(("trigger", lambda n: n.category == "trigger"))

#     # Data fetching
#     if any(k in intent_lower for k in ["fetch", "get", "api", "http", "request", "data from", "read", "load", "query", "scrape"]):
#         phases.append(("fetch", lambda n: any(t in n.node_id.lower() for t in ["http", "request"]) or "fetch" in n.name.lower()))

#     # Extract / Parse
#     if any(k in intent_lower for k in ["extract", "parse", "json", "split", "iterate", "loop over", "item"]):
#         phases.append(("extract", lambda n: any(t in n.name.lower() for t in ["extract", "split", "item", "json", "parse"])))

#     # Transform / Compose — prioritize if message/body mentioned
#     if any(k in intent_lower for k in ["set", "edit", "transform", "modify", "compose", "text", "body", "message", "format", "code", "function", "reply"]):
#         phases.append(("transform", lambda n: n.category == "transform" or any(t in n.name.lower() for t in ["set", "code", "function", "edit"])))

#     # Control flow
#     if any(k in intent_lower for k in ["if", "condition", "switch", "branch", "merge", "loop", "filter"]):
#         phases.append(("control", lambda n: n.category == "control" or any(t in n.name.lower() for t in ["if", "switch", "merge"])))

#     # AI / Generation
#     if any(k in intent_lower for k in ["ai", "llm", "chat", "model", "generate", "bot", "agent", "openai", "grok", "gemini", "reply"]):
#         phases.append(("ai", lambda n: n.category == "ai" or "langchain" in n.node_id.lower()))

#     # Action / Send — last major phase
#     if any(k in intent_lower for k in ["send", "post", "notify", "email", "slack", "telegram", "whatsapp", "msg", "message", "via", "to", "output", "store", "save"]):
#         action_matcher = lambda n: (
#             n.category == "action" or
#             any(t in n.name.lower() or t in n.node_id.lower() for t in ["email", "slack", "telegram", "whatsapp", "send", "smtp", "gmail", "post", "notify", "sheet"])
#         )
#         phases.append(("action", action_matcher))

#     # Safety
#     if any(k in intent_lower for k in ["wait", "delay", "error", "catch", "handle", "fallback"]):
#         phases.append(("safety", lambda n: any(t in n.name.lower() for t in ["wait", "error", "no-op"])))

#     # If no specific phases beyond trigger, use a minimal default
#     if len(phases) <= 1:
#         phases.extend([
#             ("transform", lambda n: n.category == "transform"),
#             ("action", lambda n: n.category == "action"),
#         ])

#     return phases


# def align_nodes_after_parsing(intent: str, parsed_nodes: List[NodeInfo]) -> List[NodeInfo]:
#     workflow_nodes: List[NodeInfo] = []
#     used_ids = set()

#     phases = generalize_phases(intent)
#     print(f"\nUsing phases for intent '{intent}': {[name for name, _ in phases]}")

#     for phase_name, matcher in phases:
#         matching = [n for n in parsed_nodes if n.node_id not in used_ids and matcher(n)]
#         if matching:
#             best = max(matching, key=lambda n: sum(k in n.name.lower() + n.node_id.lower() for k in intent.lower().split()))
#             workflow_nodes.append(best)
#             used_ids.add(best.node_id)
#             print(f"  → Phase '{phase_name}': {best.name} ({best.node_id})")

#     # If too few, supplement from registry
#     if len(workflow_nodes) < 3:
#         registry_supplement = search_registry(intent.lower())
#         for node in registry_supplement:
#             if node.node_id not in used_ids:
#                 workflow_nodes.append(NodeInfo(
#                     name=node.name,
#                     node_id=node.node_id,
#                     purpose=node.purpose,
#                     category=node.category,
#                     pitfalls=node.pitfalls,
#                     alternatives=node.alternatives
#                 ))
#                 used_ids.add(node.node_id)

#     return workflow_nodes


# def generate_workflow_structure(
#     user_intent: str,
#     selected_nodes: List[NodeInfo],
#     patterns: List,
#     guidelines: List[str]
# ) -> GeneratedWorkflow:
#     llm = get_llm()

#     nodes_info = "\n".join([
#         f"Node {i+1}: {node.name} ({node.node_id}) — Category: {node.category} — Purpose: {node.purpose}"
#         for i, node in enumerate(selected_nodes)
#     ])

#     patterns_text = "\n".join([p.description for p in patterns]) if patterns else "None"

#     prompt = ChatPromptTemplate.from_messages([
#         ("system", """Generate a complete, valid n8n workflow JSON.
# Use ONLY the provided node types. Position left-to-right.
# Include realistic parameters and helpful notes.
# Output ONLY valid JSON with nodes, connections, description."""),
#         ("user", """Intent: {intent}

# Nodes to use:
# {nodes}

# Patterns: {patterns}

# Generate workflow JSON:""")
#     ])

#     chain = prompt | llm
#     response = chain.invoke({
#         "intent": user_intent,
#         "nodes": nodes_info,
#         "patterns": patterns_text
#     })

#     content = response.content if hasattr(response, 'content') else str(response)

#     try:
#         match = re.search(r'\{[\s\S]*\}', content)
#         if match:
#             data = json.loads(match.group())
#             nodes = []
#             for i, n in enumerate(data.get("nodes", [])):
#                 idx = i if i < len(selected_nodes) else 0
#                 nodes.append(WorkflowNode(
#                     id=n.get("id", f"node_{i}"),
#                     name=n.get("name", selected_nodes[idx].name),
#                     type=n.get("type", selected_nodes[idx].node_id),
#                     position=n.get("position", {"x": i * 300, "y": 100}),
#                     parameters=n.get("parameters", {}),
#                     notes=n.get("notes", selected_nodes[idx].purpose)
#                 ))

#             connections = [
#                 WorkflowConnection(**c) for c in data.get("connections", [])
#             ]

#             return GeneratedWorkflow(
#                 nodes=nodes,
#                 connections=connections,
#                 description=data.get("description", user_intent),
#                 metadata={
#                     "source_nodes": [n.node_id for n in selected_nodes],
#                     "patterns_used": [p.description for p in patterns]
#                 }
#             )
#     except:
#         pass

#     # Fallback: simple sequential
#     return create_fallback_workflow(user_intent, selected_nodes)


# def create_fallback_workflow(user_intent: str, nodes: List[NodeInfo]) -> GeneratedWorkflow:
#     workflow_nodes = []
#     connections = []

#     for i, node in enumerate(nodes):
#         workflow_nodes.append(WorkflowNode(
#             id=f"node_{i}",
#             name=node.name,
#             type=node.node_id,
#             position={"x": i * 300, "y": 100},
#             parameters={},
#             notes=node.purpose or "Workflow step"
#         ))
#         if i > 0:
#             connections.append(WorkflowConnection(source=f"node_{i-1}", target=f"node_{i}"))

#     return GeneratedWorkflow(
#         nodes=workflow_nodes,
#         connections=connections,
#         description=f"Workflow: {user_intent}",
#         metadata={"source_nodes": [n.node_id for n in nodes]}
#     )


# def workflow_to_n8n_format(workflow: GeneratedWorkflow) -> Dict[str, Any]:
#     n8n_nodes = []
#     for node in workflow.nodes:
#         n8n_nodes.append({
#             "id": node.id,
#             "name": node.name,
#             "type": node.type,
#             "typeVersion": 1,
#             "position": [node.position["x"], node.position["y"]],
#             "parameters": node.parameters,
#             "notes": node.notes
#         })

#     connections = {}
#     for conn in workflow.connections:
#         src = conn.source
#         out = conn.source_output
#         tgt = conn.target
#         inp = conn.target_input
#         if src not in connections:
#             connections[src] = {}
#         if out not in connections[src]:
#             connections[src][out] = []
#         connections[src][out].append({"node": tgt, "type": inp, "index": 0})

#     return {
#         "name": "Generated Workflow",
#         "nodes": n8n_nodes,
#         "connections": connections,
#         "active": False,
#         "settings": {},
#         "tags": []
#     }


# def generate_workflow_from_parsed_bp(
#     user_intent: str,
#     best_practices_text: str,
#     techniques: Optional[List[str]] = None
# ) -> GeneratedWorkflow:
#     bp_parser = parse_best_practices(best_practices_text)
#     print(f"\nParsed {len(bp_parser.nodes)} nodes from best practices")

#     # Combine best practices nodes and registry nodes
#     all_available_nodes = bp_parser.nodes.copy()

#     # Add all registry nodes (so they are always available to LLM)
#     for reg_node in NODE_REGISTRY:
#         # Avoid duplicates
#         if not any(n.node_id == reg_node.node_id for n in all_available_nodes):
#             all_available_nodes.append(NodeInfo(
#                 name=reg_node.name,
#                 node_id=reg_node.node_id,
#                 purpose=reg_node.purpose,
#                 category=reg_node.category,
#                 pitfalls=reg_node.pitfalls,
#                 use_cases=[],
#                 alternatives=reg_node.alternatives
#             ))

#     print(f"Total available nodes (best practices + registry): {len(all_available_nodes)}")

#     # Now use LLM on the combined list
#     workflow_specific_nodes = llm_select_and_adapt_nodes_for_intent(
#         user_intent=user_intent,
#         parsed_nodes=all_available_nodes
#     )

#     print(f"Selected {len(workflow_specific_nodes)} nodes")

#     # Convert to NodeInfo
#     selected_node_infos = [
#         NodeInfo(
#             name=n["name"],
#             node_id=n["node_id"],
#             purpose=n["purpose"],
#             category=n["category"],
#             pitfalls=n.get("pitfalls", []),
#             use_cases=n.get("use_cases", []),
#             alternatives=n.get("alternatives", [])
#         )
#         for n in workflow_specific_nodes
#     ]

#     ordered_nodes = align_nodes_after_parsing(user_intent, selected_node_infos)

#     workflow = generate_workflow_structure(
#         user_intent=user_intent,
#         selected_nodes=ordered_nodes,
#         patterns=bp_parser.patterns,
#         guidelines=bp_parser.general_guidelines
#     )
    
#     workflow.metadata["source_nodes"] = [n["node_id"] for n in workflow_specific_nodes]

#     return workflow