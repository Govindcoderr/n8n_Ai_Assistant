# backend/mytools/registry_node_generator.py - UPGRADED

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from backend.mytools.node_registry import (
    NODE_REGISTRY, 
    search_registry, 
    get_nodes_by_category,
    format_node_for_api,
    RegistryNode
)

@dataclass
class WorkflowRequirements:
    """What the workflow needs based on intent analysis"""
    trigger_keywords: List[str]
    action_keywords: List[str]
    processing_keywords: List[str]
    platform_keywords: List[str]
    data_keywords: List[str]
    integration_keywords: List[str]
    raw_intent: str


def analyze_workflow_requirements(user_intent: str) -> WorkflowRequirements:
    """Enhanced intent analysis with comprehensive keyword detection"""
    intent_lower = user_intent.lower()
    
    # === TRIGGER DETECTION ===
    trigger_keywords = []
    
    if any(w in intent_lower for w in ["webhook", "receive", "incoming", "listen", "api call", "http post", "http get"]):
        trigger_keywords.append("webhook")
    
    if any(w in intent_lower for w in ["schedule", "daily", "weekly", "hourly", "every", "cron", "periodic", "regularly", "automated"]):
        trigger_keywords.append("schedule")
    
    if any(w in intent_lower for w in ["chat", "message", "bot", "conversation", "chatbot", "ask", "answer"]):
        trigger_keywords.append("chat")
    
    if any(w in intent_lower for w in ["email received", "new email", "inbox", "when email"]):
        trigger_keywords.append("email")
    
    if any(w in intent_lower for w in ["form", "submission", "submit", "input"]):
        trigger_keywords.append("form")
    
    if not trigger_keywords or any(w in intent_lower for w in ["create", "generate", "build", "make"]):
        trigger_keywords.insert(0, "manual")
    
    # === ACTION KEYWORDS ===
    action_keywords = []
    
    # Communication
    if any(w in intent_lower for w in ["send email", "email", "mail"]):
        action_keywords.append("email")
    if any(w in intent_lower for w in ["slack", "post to slack"]):
        action_keywords.append("slack")
    if any(w in intent_lower for w in ["telegram"]):
        action_keywords.append("telegram")
    
    # Data sources
    if any(w in intent_lower for w in ["youtube", "video"]):
        action_keywords.append("youtube")
    if any(w in intent_lower for w in ["scrape", "crawl", "extract from web", "web data"]):
        action_keywords.append("scraping")
    if any(w in intent_lower for w in ["fetch", "get data", "download", "retrieve", "api"]):
        action_keywords.append("http")
    
    # Data storage
    if any(w in intent_lower for w in ["sheets", "spreadsheet", "google sheets", "excel"]):
        action_keywords.append("sheets")
    if any(w in intent_lower for w in ["database", "postgres", "mysql", "sql", "db", "store in"]):
        action_keywords.append("database")
    
    # AI/LLM
    if any(w in intent_lower for w in ["generate", "create content", "ai", "llm", "claude", "gpt", "write", "compose", "summarize"]):
        action_keywords.append("ai")
    
    # === PROCESSING KEYWORDS ===
    processing_keywords = []
    
    if any(w in intent_lower for w in ["extract", "parse", "get from", "pull out"]):
        processing_keywords.append("extract")
    if any(w in intent_lower for w in ["transform", "modify", "change", "format", "convert", "set", "edit", "compose", "append", "update", "prepare"]):
        processing_keywords.append("transform")
    if any(w in intent_lower for w in ["if", "when", "condition", "check", "filter"]):
        processing_keywords.append("condition")
    if any(w in intent_lower for w in ["reply", "respond", "answer", "send back"]):
        processing_keywords.append("respond")
    
    # === DATA & PLATFORM KEYWORDS ===
    data_keywords = []
    if any(w in intent_lower for w in ["json", "data structure", "object"]):
        data_keywords.append("json")
    if any(w in intent_lower for w in ["csv", "spreadsheet data"]):
        data_keywords.append("csv")
    
    integration_keywords = []
    if any(w in intent_lower for w in ["integrate", "connect", "sync", "push to", "send to"]):
        integration_keywords.append("integration")
    
    platform_keywords = []
    platforms = {
        "youtube": ["youtube", "video"],
        "slack": ["slack"],
        "telegram": ["telegram"],
        "email": ["email", "gmail", "smtp"],
        "sheets": ["sheets", "spreadsheet", "google sheets"],
        "claude": ["claude", "anthropic"],
        "openai": ["openai", "gpt", "chatgpt"],
        "gemini": ["gemini", "google ai"],
    }
    
    for platform, keywords in platforms.items():
        if any(k in intent_lower for k in keywords):
            platform_keywords.append(platform)
    
    return WorkflowRequirements(
        trigger_keywords=trigger_keywords,
        action_keywords=action_keywords,
        processing_keywords=processing_keywords,
        platform_keywords=platform_keywords,
        data_keywords=data_keywords,
        integration_keywords=integration_keywords,
        raw_intent=user_intent
    )


def select_nodes_from_registry(requirements: WorkflowRequirements) -> List[Dict[str, Any]]:
    """Enhanced node selection with full metadata"""
    selected_nodes = []
    used_ids = set()
    
    # === 1. SELECT TRIGGER ===
    trigger_node = None
    for trigger_kw in requirements.trigger_keywords:
        candidates = search_registry(trigger_kw)
        trigger_candidates = [n for n in candidates if n.category == "trigger"]
        if trigger_candidates:
            trigger_node = trigger_candidates[0]
            break
    
    if trigger_node:
        node_data = format_node_for_api(trigger_node)
        node_data["purpose"] = f"Triggers workflow - {trigger_node.purpose}"
        node_data["is_recommended"] = True
        selected_nodes.append(node_data)
        used_ids.add(trigger_node.node_id)
    
    # === 2. SELECT DATA FETCHING ===
    if ("http" in requirements.action_keywords or 
        "scraping" in requirements.action_keywords):
        
        http_nodes = search_registry("http request")
        if http_nodes and http_nodes[0].node_id not in used_ids:
            node = http_nodes[0]
            node_data = format_node_for_api(node)
            node_data["purpose"] = "Fetches data from API or external source"
            node_data["is_recommended"] = True
            selected_nodes.append(node_data)
            used_ids.add(node.node_id)
    
    # === 3. SELECT AI NODES ===
    if "ai" in requirements.action_keywords:
        for platform in requirements.platform_keywords:
            if platform in ["claude", "openai", "gemini"]:
                ai_nodes = search_registry(platform)
                ai_candidates = [n for n in ai_nodes if n.category == "ai" and n.node_id not in used_ids]
                if ai_candidates:
                    node = ai_candidates[0]
                    node_data = format_node_for_api(node)
                    node_data["purpose"] = f"Generates content using {platform} AI"
                    node_data["is_recommended"] = True
                    selected_nodes.append(node_data)
                    used_ids.add(node.node_id)
                    break
    
    # === 4. SELECT TRANSFORM NODES ===
    if "transform" in requirements.processing_keywords:
        transform_nodes = search_registry("set edit")
        for node in transform_nodes:
            if "set" in node.name.lower() and node.node_id not in used_ids:
                node_data = format_node_for_api(node)
                node_data["purpose"] = "Transforms and prepares data"
                node_data["is_recommended"] = True
                selected_nodes.append(node_data)
                used_ids.add(node.node_id)
                break
    
    # === 5. SELECT RESPOND NODE ===
    if "respond" in requirements.processing_keywords or "chat" in requirements.trigger_keywords:
        respond_nodes = search_registry("respond chat")
        for node in respond_nodes:
            if "respond" in node.name.lower() and node.node_id not in used_ids:
                node_data = format_node_for_api(node)
                node_data["purpose"] = "Sends response back to user in chat"
                node_data["is_recommended"] = True
                selected_nodes.append(node_data)
                used_ids.add(node.node_id)
                break
    
    # === 6. SELECT OUTPUT NODES ===
    for action_kw in requirements.action_keywords:
        if action_kw in ["email", "slack", "telegram", "youtube", "sheets"]:
            action_nodes = search_registry(action_kw)
            for node in action_nodes[:1]:
                if node.node_id not in used_ids and node.category == "action":
                    node_data = format_node_for_api(node)
                    node_data["is_recommended"] = True
                    selected_nodes.append(node_data)
                    used_ids.add(node.node_id)
                    break
    return selected_nodes


def generate_workflow_nodes_from_registry(user_intent: str) -> List[Dict[str, Any]]:
    """Main function: Generate workflow-specific nodes using registry"""
    print(f"\n🔍 Analyzing intent: {user_intent}")
    
    requirements = analyze_workflow_requirements(user_intent)
    
    print(f"   Triggers: {requirements.trigger_keywords}")
    print(f"   Actions: {requirements.action_keywords}")
    print(f"   Processing: {requirements.processing_keywords}")
    print(f"   Platforms: {requirements.platform_keywords}")
    
    workflow_nodes = select_nodes_from_registry(requirements)
    
    print(f"\n✅ Selected {len(workflow_nodes)} nodes:")
    for node in workflow_nodes:
        print(f"   • {node['name']} ({node['category']}) - {node['purpose']}")
    
    return workflow_nodes


def format_workflow_nodes_for_api(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format nodes for API response WITH inferred connections"""
    formatted = []
    
    for i, node in enumerate(nodes):
        # Infer connections based on sequential order
        input_conns = []
        output_conns = []
        
        if i > 0:
            input_conns.append(nodes[i-1]["name"])
        if i < len(nodes) - 1:
            output_conns.append(nodes[i+1]["name"])
        
        # Use existing structure and add connections
        formatted_node = node.copy()
        formatted_node["input_connections"] = input_conns
        formatted_node["output_connections"] = output_conns
        
        formatted.append(formatted_node)
    
    return formatted