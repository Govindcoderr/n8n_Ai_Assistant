import re
from typing import Dict, List, Set, Any


# ============================================================
# STAGE 1 — STRUCTURED BEST PRACTICE PARSING
# ============================================================

def parse_best_practices(text: str) -> Dict[str, Any]:
    t = text.lower()

    model = {
        "phases": set(),
        "mandatory": set(),
        "recommended": set(),
        "providers": set(),
    }

    # ---- Phases ----
    if re.search(r"(trigger|webhook|schedule)", t):
        model["phases"].add("trigger")

    if re.search(r"(fetch|scrape|http request)", t):
        model["phases"].add("data_retrieval")

    if re.search(r"(generate|generation|ai|model)", t):
        model["phases"].add("generation")

    if re.search(r"(notify|notification|email|slack|whatsapp)", t):
        model["phases"].add("notification")

    if re.search(r"(store|database|sheets|excel)", t):
        model["phases"].add("storage")

    # ---- Mandatory language ----
    if re.search(r"(must|always|required)", t):
        if "generation" in model["phases"]:
            model["mandatory"].add("generation")
        if "trigger" in model["phases"]:
            model["mandatory"].add("trigger")

    # ---- Providers ----
    for provider in ["openai", "google gemini", "elevenlabs", "twilio", "slack"]:
        if provider in t:
            model["providers"].add(provider)

    return model


# ============================================================
# STAGE 2 — ABSTRACT WORKFLOW PLAN
# ============================================================

def build_workflow_plan(bp_model: Dict[str, Any]) -> List[Dict[str, Any]]:
    plan = []

    for phase in ["trigger", "data_retrieval", "generation", "notification", "storage"]:
        if phase in bp_model["phases"]:
            plan.append({
                "phase": phase,
                "required": phase in bp_model["mandatory"]
            })

    return plan


# ============================================================
# STAGE 3 — INTENT BINDING
# ============================================================

def bind_intent(plan: List[Dict[str, Any]], intent: str) -> List[Dict[str, Any]]:
    intent = intent.lower()

    bound = []

    for step in plan:
        if step["phase"] == "generation":
            if "image" in intent:
                step["variant"] = "image"
            elif "video" in intent:
                step["variant"] = "video"
            else:
                step["variant"] = "text"

        if step["phase"] == "notification":
            if any(k in intent for k in ["notify", "send", "alert", "whatsapp"]):
                bound.append(step)
            elif step["required"]:
                bound.append(step)
        else:
            bound.append(step)

    return bound


# ============================================================
# STAGE 4 — WORKFLOW NODE EMISSION
# ============================================================

def emit_nodes(plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    nodes = []
    idx = 1

    for step in plan:
        node = {"id": f"node_{idx}", "role": None, "name": None}

        if step["phase"] == "trigger":
            node.update({"name": "Manual Trigger", "role": "trigger"})

        elif step["phase"] == "data_retrieval":
            node.update({"name": "HTTP Request", "role": "source"})

        elif step["phase"] == "generation":
            if step.get("variant") == "image":
                node.update({"name": "Image Generator", "role": "processor"})
            else:
                node.update({"name": "AI Model", "role": "processor"})

        elif step["phase"] == "notification":
            node.update({"name": "Notification", "role": "sink"})

        elif step["phase"] == "storage":
            node.update({"name": "Database", "role": "sink"})

        nodes.append(node)
        idx += 1

    return nodes


# ============================================================
# ORCHESTRATOR
# ============================================================

def search_node_engine(intent: str, best_practice_text: str) -> Dict[str, Any]:
    bp_model = parse_best_practices(best_practice_text)
    plan = build_workflow_plan(bp_model)
    bound_plan = bind_intent(plan, intent)
    nodes = emit_nodes(bound_plan)

    return {
        "intent": intent,
        "workflow_plan": bound_plan,
        "workflow_nodes": nodes
    }
