# backend/mytools/node_registry.py - UPGRADED with Full n8n Node Data

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

@dataclass
class NodeCodex:
    """Documentation and resource links for a node"""
    categories: List[str] = field(default_factory=list)
    primary_documentation: List[str] = field(default_factory=list)
    credential_documentation: List[str] = field(default_factory=list)


@dataclass
class RegistryNode:
    """Full n8n node metadata"""
    # Core identifiers
    uuid: str
    key: str  # Full node ID like "n8n-nodes-base.httpRequest"
    node_id: str  # Same as key for backward compatibility
    
    # Display properties
    name: str
    display_name: str
    description: str
    subcategory: str
    
    # Node behavior
    group: List[str]  # e.g., ["transform", "trigger"]
    outputs: List[str]  # e.g., ["main"]
    icon_url: Optional[str] = None
    
    # Documentation
    codex: Optional[NodeCodex] = None
    
    # Our custom metadata (for workflow generation)
    category: str = "action"  # Our simplified category: trigger/action/transform/control/ai
    purpose: str = ""
    pitfalls: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    input_connections: List[str] = field(default_factory=list)
    output_connections: List[str] = field(default_factory=list)
    
    # Additional n8n metadata
    type: str = "node"
    
    def __post_init__(self):
        """Ensure defaults and derive category if needed"""
        if not self.node_id:
            self.node_id = self.key
        
        # Auto-derive category from group if not set
        if self.category == "action" and self.group:
            if "trigger" in self.group:
                self.category = "trigger"
            elif any(t in self.group for t in ["transform", "data"]):
                self.category = "transform"
    
    @classmethod
    def from_n8n_data(cls, data: Dict[str, Any], our_metadata: Dict[str, Any] = None):
        """Create RegistryNode from n8n API data"""
        props = data.get("properties", {})
        defaults = props.get("defaults", {})
        codex_data = props.get("codex", {})
        
        # Parse codex
        codex = None
        if codex_data:
            resources = codex_data.get("resources", {})
            codex = NodeCodex(
                categories=codex_data.get("categories", []),
                primary_documentation=[
                    doc.get("url", "") for doc in resources.get("primaryDocumentation", [])
                ],
                credential_documentation=[
                    doc.get("url", "") for doc in resources.get("credentialDocumentation", [])
                ]
            )
        
        # Our custom metadata
        meta = our_metadata or {}
        
        return cls(
            uuid=data.get("uuid", ""),
            key=data.get("key", ""),
            node_id=data.get("key", ""),
            name=defaults.get("name", props.get("name", "")),
            display_name=props.get("displayName", ""),
            description=props.get("description", ""),
            subcategory=data.get("subcategory", "*"),
            group=props.get("group", []),
            outputs=props.get("outputs", ["main"]),
            icon_url=props.get("iconUrl"),
            codex=codex,
            category=meta.get("category", "action"),
            purpose=meta.get("purpose", props.get("description", "")),
            pitfalls=meta.get("pitfalls", []),
            alternatives=meta.get("alternatives", []),
            type=data.get("type", "node")
        )


# Comprehensive registry with full n8n data + our custom metadata
# Format: n8n data + our workflow generation metadata
NODE_REGISTRY: List[RegistryNode] = [
    # ============= TRIGGERS =============
    RegistryNode(
        uuid="trigger-manual-001",
        key="n8n-nodes-base.manualTrigger",
        node_id="n8n-nodes-base.manualTrigger",
        name="Manual Trigger",
        display_name="Manual Trigger",
        description="Manually start workflow for testing",
        subcategory="Core",
        group=["trigger"],
        outputs=["main"],
        category="trigger",
        purpose="Manually start workflow for testing and one-off executions"
    ),
    
    RegistryNode(
        uuid="trigger-webhook-001",
        key="n8n-nodes-base.webhook",
        node_id="n8n-nodes-base.webhook",
        name="Webhook",
        display_name="Webhook",
        description="Trigger workflow on incoming HTTP requests",
        subcategory="Core",
        group=["trigger"],
        outputs=["main"],
        icon_url="icons/n8n-nodes-base/dist/nodes/Webhook/webhook.svg",
        category="trigger",
        purpose="Trigger on incoming HTTP requests (GET/POST/etc)",
        pitfalls=["Remember to activate workflow for webhook to work", "Webhook URL changes when workflow is renamed"]
    ),
    
    RegistryNode(
        uuid="trigger-schedule-001",
        key="n8n-nodes-base.scheduleTrigger",
        node_id="n8n-nodes-base.scheduleTrigger",
        name="Schedule Trigger",
        display_name="Schedule Trigger",
        description="Advanced scheduling with timezone support",
        subcategory="Core",
        group=["trigger"],
        outputs=["main"],
        category="trigger",
        purpose="Advanced scheduling with timezone support"
    ),
    
    RegistryNode(
        uuid="trigger-chat-001",
        key="@n8n/n8n-nodes-langchain.chatTrigger",
        node_id="@n8n/n8n-nodes-langchain.chatTrigger",
        name="Chat Trigger",
        display_name="Chat Trigger",
        description="Start workflow from chat message",
        subcategory="Langchain",
        group=["trigger"],
        outputs=["main"],
        category="trigger",
        purpose="Start workflow from chat message in chat interfaces"
    ),
    
    # ============= CORE ACTIONS =============
    RegistryNode(
        uuid="action-http-001",
        key="n8n-nodes-base.httpRequest",
        node_id="n8n-nodes-base.httpRequest",
        name="HTTP Request",
        display_name="HTTP Request",
        description="Call any REST API",
        subcategory="Core",
        group=["transform"],
        outputs=["main"],
        icon_url="icons/n8n-nodes-base/dist/nodes/HttpRequest/httprequest.svg",
        codex=NodeCodex(
            categories=["Development", "Core Nodes"],
            primary_documentation=["https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/"]
        ),
        category="action",
        purpose="Call any REST API, fetch data from web services",
        pitfalls=["Always handle authentication properly", "Check rate limits of target API"]
    ),
    
    RegistryNode(
        uuid="transform-set-001",
        key="n8n-nodes-base.set",
        node_id="n8n-nodes-base.set",
        name="Edit Fields (Set)",
        display_name="Edit Fields (Set)",
        description="Add, modify, or remove data fields",
        subcategory="Core",
        group=["transform"],
        outputs=["main"],
        category="transform",
        purpose="Add, modify, or remove data fields in items"
    ),
    
    RegistryNode(
        uuid="transform-code-001",
        key="n8n-nodes-base.code",
        node_id="n8n-nodes-base.code",
        name="Code",
        display_name="Code",
        description="Execute custom JavaScript/Python code",
        subcategory="Core",
        group=["transform"],
        outputs=["main"],
        category="transform",
        purpose="Execute custom JavaScript/Python code for complex logic",
        pitfalls=["Code runs in sandbox, limited libraries available"]
    ),
    
    # ============= CONTROL FLOW =============
    RegistryNode(
        uuid="control-if-001",
        key="n8n-nodes-base.if",
        node_id="n8n-nodes-base.if",
        name="If",
        display_name="If",
        description="Conditional branching",
        subcategory="Core",
        group=["transform"],
        outputs=["main"],
        category="control",
        purpose="Conditional branching based on data values"
    ),
    
    RegistryNode(
        uuid="control-switch-001",
        key="n8n-nodes-base.switch",
        node_id="n8n-nodes-base.switch",
        name="Switch",
        display_name="Switch",
        description="Multi-way branching",
        subcategory="Core",
        group=["transform"],
        outputs=["main"],
        category="control",
        purpose="Multi-way branching based on conditions"
    ),
    
    RegistryNode(
        uuid="control-merge-001",
        key="n8n-nodes-base.merge",
        node_id="n8n-nodes-base.merge",
        name="Merge",
        display_name="Merge",
        description="Combine data from multiple branches",
        subcategory="Core",
        group=["transform"],
        outputs=["main"],
        category="control",
        purpose="Combine data from multiple branches/inputs"
    ),
    
    # ============= AI/LANGCHAIN NODES =============
    RegistryNode(
        uuid="ai-claude-001",
        key="@n8n/n8n-nodes-langchain.lmChatAnthropic",
        node_id="@n8n/n8n-nodes-langchain.lmChatAnthropic",
        name="Anthropic Claude",
        display_name="Anthropic Chat Model",
        description="Claude 3.5 Sonnet, Opus, Haiku models",
        subcategory="Langchain",
        group=["transform"],
        outputs=["main"],
        codex=NodeCodex(
            categories=["AI", "Langchain"],
            primary_documentation=["https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.lmchatanthropic/"]
        ),
        category="ai",
        purpose="Claude 3.5 Sonnet, Opus, Haiku models for reasoning"
    ),
    
    RegistryNode(
        uuid="ai-openai-001",
        key="@n8n/n8n-nodes-langchain.lmChatOpenAi",
        node_id="@n8n/n8n-nodes-langchain.lmChatOpenAi",
        name="OpenAI Chat Model",
        display_name="OpenAI Chat Model",
        description="GPT-4, GPT-4o, GPT-3.5 chat models",
        subcategory="Langchain",
        group=["transform"],
        outputs=["main"],
        category="ai",
        purpose="GPT-4, GPT-4o, GPT-3.5 chat models"
    ),
    
    RegistryNode(
        uuid="ai-gemini-001",
        key="@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
        node_id="@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
        name="Google Gemini",
        display_name="Google Gemini Chat Model",
        description="Gemini Pro, Ultra multimodal AI models",
        subcategory="Langchain",
        group=["transform"],
        outputs=["main"],
        category="ai",
        purpose="Gemini Pro, Ultra multimodal AI models"
    ),
    
    RegistryNode(
        uuid="ai-respond-001",
        key="@n8n/n8n-nodes-langchain.respondToChat",
        node_id="@n8n/n8n-nodes-langchain.respondToChat",
        name="Respond to Chat",
        display_name="Respond to Chat",
        description="Send AI response back to chat",
        subcategory="Langchain",
        group=["transform"],
        outputs=["main"],
        category="action",
        purpose="Send AI response back to chat interface"
    ),
    
    # ============= COMMUNICATION =============
    RegistryNode(
        uuid="comm-slack-001",
        key="n8n-nodes-base.slack",
        node_id="n8n-nodes-base.slack",
        name="Slack",
        display_name="Slack",
        description="Send messages to Slack",
        subcategory="Communication",
        group=["transform"],
        outputs=["main"],
        icon_url="icons/n8n-nodes-base/dist/nodes/Slack/slack.svg",
        codex=NodeCodex(
            categories=["Communication"],
            primary_documentation=["https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.slack/"]
        ),
        category="action",
        purpose="Send messages, manage channels, files in Slack"
    ),
    
    RegistryNode(
        uuid="comm-email-001",
        key="n8n-nodes-base.email",
        node_id="n8n-nodes-base.email",
        name="Email",
        display_name="Send Email",
        description="Send emails via SMTP",
        subcategory="Communication",
        group=["transform"],
        outputs=["main"],
        category="action",
        purpose="Send emails via SMTP"
    ),
    
    RegistryNode(
        uuid="comm-telegram-001",
        key="n8n-nodes-base.telegram",
        node_id="n8n-nodes-base.telegram",
        name="Telegram",
        display_name="Telegram",
        description="Send Telegram messages",
        subcategory="Communication",
        group=["transform"],
        outputs=["main"],
        category="action",
        purpose="Send messages, photos, files via Telegram Bot API"
    ),
    
    # ============= DATA & STORAGE =============
    RegistryNode(
        uuid="data-sheets-001",
        key="n8n-nodes-base.googleSheets",
        node_id="n8n-nodes-base.googleSheets",
        name="Google Sheets",
        display_name="Google Sheets",
        description="Read/write Google Sheets",
        subcategory="Productivity",
        group=["transform"],
        outputs=["main"],
        icon_url="icons/n8n-nodes-base/dist/nodes/Google/Sheets/googleSheets.svg",
        codex=NodeCodex(
            categories=["Productivity", "Data & Storage"],
            primary_documentation=["https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.googlesheets/"]
        ),
        category="action",
        purpose="Read/write/update Google Sheets spreadsheets"
    ),
    
    RegistryNode(
        uuid="data-postgres-001",
        key="n8n-nodes-base.postgres",
        node_id="n8n-nodes-base.postgres",
        name="PostgreSQL",
        display_name="Postgres",
        description="Execute SQL queries on PostgreSQL",
        subcategory="Data & Storage",
        group=["transform"],
        outputs=["main"],
        category="action",
        purpose="Execute SQL queries on PostgreSQL databases"
    ),
    
    # ============= SOCIAL & CONTENT =============
    RegistryNode(
        uuid="social-youtube-001",
        key="n8n-nodes-base.youtube",
        node_id="n8n-nodes-base.youtube",
        name="YouTube",
        display_name="YouTube",
        description="Manage YouTube videos and channels",
        subcategory="Marketing",
        group=["transform"],
        outputs=["main"],
        icon_url="icons/n8n-nodes-base/dist/nodes/YouTube/youtube.svg",
        codex=NodeCodex(
            categories=["Marketing", "Social Media"],
            primary_documentation=["https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.youtube/"]
        ),
        category="action",
        purpose="Get video details, manage channel, playlists"
    ),
]

# Build lookup dictionaries
NODE_BY_ID = {node.node_id: node for node in NODE_REGISTRY}
NODE_BY_UUID = {node.uuid: node for node in NODE_REGISTRY}
NODE_BY_KEY = {node.key: node for node in NODE_REGISTRY}

def search_registry(keyword: str) -> List[RegistryNode]:
    """Search registry by keyword in name, purpose, category, or node_id"""
    keyword = keyword.lower()
    return [
        node for node in NODE_REGISTRY
        if (keyword in node.name.lower() or 
            keyword in node.display_name.lower() or
            keyword in node.purpose.lower() or 
            keyword in node.node_id.lower() or
            keyword in node.description.lower() or
            keyword in node.category.lower())
    ]

def get_nodes_by_category(category: str) -> List[RegistryNode]:
    """Get all nodes in a specific category"""
    return [node for node in NODE_REGISTRY if node.category == category]

def get_nodes_by_group(group: str) -> List[RegistryNode]:
    """Get nodes by n8n group (trigger, transform, etc)"""
    return [node for node in NODE_REGISTRY if group in node.group]

def get_nodes_by_codex_category(codex_category: str) -> List[RegistryNode]:
    """Get nodes by codex category (AI, Marketing, etc)"""
    return [
        node for node in NODE_REGISTRY 
        if node.codex and codex_category in node.codex.categories
    ]

def get_ai_nodes() -> List[RegistryNode]:
    """Get all AI/LLM nodes"""
    return get_nodes_by_category("ai")

def get_trigger_nodes() -> List[RegistryNode]:
    """Get all trigger nodes"""
    return get_nodes_by_category("trigger")

def suggest_nodes(task_description: str) -> List[RegistryNode]:
    """Suggest relevant nodes based on task description"""
    keywords = task_description.lower().split()
    scored_nodes = []
    
    for node in NODE_REGISTRY:
        score = 0
        searchable = f"{node.name} {node.display_name} {node.purpose} {node.description} {node.category}".lower()
        
        # Add codex categories to search
        if node.codex:
            searchable += " " + " ".join(node.codex.categories).lower()
        
        for keyword in keywords:
            if keyword in searchable:
                score += 1
        
        if score > 0:
            scored_nodes.append((score, node))
    
    # Sort by score descending
    scored_nodes.sort(reverse=True, key=lambda x: x[0])
    return [node for score, node in scored_nodes[:10]]

def get_node_documentation(node_id: str) -> Dict[str, Any]:
    """Get documentation URLs for a node"""
    node = NODE_BY_ID.get(node_id)
    if not node or not node.codex:
        return {"primary": [], "credentials": []}
    
    return {
        "primary": node.codex.primary_documentation,
        "credentials": node.codex.credential_documentation
    }

def format_node_for_api(node: RegistryNode) -> Dict[str, Any]:
    """Format node for API response with all metadata"""
    return {
        "uuid": node.uuid,
        "key": node.key,
        "node_id": node.node_id,
        "name": node.name,
        "display_name": node.display_name,
        "description": node.description,
        "category": node.category,
        "group": node.group,
        "outputs": node.outputs,
        "icon_url": node.icon_url,
        "purpose": node.purpose,
        "pitfalls": node.pitfalls,
        "alternatives": node.alternatives,
        "codex_categories": node.codex.categories if node.codex else [],
        "documentation": get_node_documentation(node.node_id),
        "subcategory": node.subcategory
    }