# from typing import List

# from backend.mytypes.categorization import WorkflowTechnique

# # LLM → Enum mapping
# TECHNIQUE_NORMALIZATION_MAP = {
#     # Scheduling
#     "Scheduled Automation": WorkflowTechnique.SCHEDULING,
#     "Cron / Calendar Trigger (last weekend of each month)": WorkflowTechnique.SCHEDULING,
#     "Scheduled triggers (cron/recurring jobs)": WorkflowTechnique.SCHEDULING,
#     "Scheduled Triggers (Cron/Recurrence)": WorkflowTechnique.SCHEDULING,
#     "Recurring Workflow Orchestration": WorkflowTechnique.SCHEDULING,

#     # Messaging / Notifications
#     "Messaging Integration (email/SMS)": WorkflowTechnique.NOTIFICATION,
#     "Automated messaging": WorkflowTechnique.NOTIFICATION,
#     "Automated Messaging": WorkflowTechnique.NOTIFICATION,
#     "Customer Follow‑up Automation": WorkflowTechnique.NOTIFICATION,

#     # CRM / Data
#     "CRM / Customer Data Integration": WorkflowTechnique.KNOWLEDGE_BASE,
#     "CRM / Messaging Platform Integration": WorkflowTechnique.KNOWLEDGE_BASE,

#     # AI
#     "AI text generation (natural language generation)": WorkflowTechnique.CONTENT_GENERATION,
# }


# def normalize_techniques(
#     raw_techniques: List[str]
# ) -> List[WorkflowTechnique]:
#     normalized: List[WorkflowTechnique] = []

#     for technique in raw_techniques:
#         enum_value = TECHNIQUE_NORMALIZATION_MAP.get(technique)
#         if enum_value:
#             normalized.append(enum_value)

#     # remove duplicates
#     return list(set(normalized))


from typing import List
from backend.mytypes.categorization import WorkflowTechnique


KEYWORD_TECHNIQUE_MAP = {
    # Scheduling
    "schedule": WorkflowTechnique.SCHEDULING,
    "scheduled": WorkflowTechnique.SCHEDULING,
    "cron": WorkflowTechnique.SCHEDULING,
    "recurring": WorkflowTechnique.SCHEDULING,
    "automation": WorkflowTechnique.SCHEDULING,
    "orchestration": WorkflowTechnique.SCHEDULING,
    "trigger": WorkflowTechnique.SCHEDULING,
    "time-based": WorkflowTechnique.SCHEDULING,
    "time based": WorkflowTechnique.SCHEDULING,
    "periodic": WorkflowTechnique.SCHEDULING,
    "interval": WorkflowTechnique.SCHEDULING,
    "calendar": WorkflowTechnique.SCHEDULING,
    "reminders": WorkflowTechnique.SCHEDULING,
    "reminder": WorkflowTechnique.SCHEDULING,
    "timed": WorkflowTechnique.SCHEDULING,
    "batch": WorkflowTechnique.SCHEDULING,
    "nightly": WorkflowTechnique.SCHEDULING,
    "daily": WorkflowTechnique.SCHEDULING,
    "weekly": WorkflowTechnique.SCHEDULING,
    "monthly": WorkflowTechnique.SCHEDULING,
    "yearly": WorkflowTechnique.SCHEDULING,
    "hourly": WorkflowTechnique.SCHEDULING,
    "every": WorkflowTechnique.SCHEDULING,
    "at": WorkflowTechnique.SCHEDULING,
    "on the": WorkflowTechnique.SCHEDULING,
    "each": WorkflowTechnique.SCHEDULING,
    "end of": WorkflowTechnique.SCHEDULING,
    "beginning of": WorkflowTechnique.SCHEDULING,
    "start of": WorkflowTechnique.SCHEDULING,
    "weekend": WorkflowTechnique.SCHEDULING,
    "weekday": WorkflowTechnique.SCHEDULING,
    "business day": WorkflowTechnique.SCHEDULING,
    "business days": WorkflowTechnique.SCHEDULING,
    "workday": WorkflowTechnique.SCHEDULING,
    "workdays": WorkflowTechnique.SCHEDULING,


    # Notification / Messaging
    "message": WorkflowTechnique.NOTIFICATION,
    "messaging": WorkflowTechnique.NOTIFICATION,
    "whatsapp": WorkflowTechnique.NOTIFICATION,
    "sms": WorkflowTechnique.NOTIFICATION,
    "email": WorkflowTechnique.NOTIFICATION,
    "instagram": WorkflowTechnique.NOTIFICATION,
    "slack": WorkflowTechnique.NOTIFICATION,
    "teams": WorkflowTechnique.NOTIFICATION,
    "telegram": WorkflowTechnique.NOTIFICATION,
    "notification": WorkflowTechnique.NOTIFICATION,
    "alert": WorkflowTechnique.NOTIFICATION,
    "notify": WorkflowTechnique.NOTIFICATION,
    "follow-up": WorkflowTechnique.NOTIFICATION,
    "follow up": WorkflowTechnique.NOTIFICATION,
    "followup": WorkflowTechnique.NOTIFICATION,
    "reminder": WorkflowTechnique.NOTIFICATION,
    "reminders": WorkflowTechnique.NOTIFICATION,
    "update": WorkflowTechnique.NOTIFICATION,
    "updates": WorkflowTechnique.NOTIFICATION,
    "broadcast": WorkflowTechnique.NOTIFICATION,
    "WhatsApp Messaging": WorkflowTechnique.NOTIFICATION,
    "announcements": WorkflowTechnique.NOTIFICATION,


    # Content Generation
    "image generation": WorkflowTechnique.CONTENT_GENERATION,
    "generate image": WorkflowTechnique.CONTENT_GENERATION,
    "text generation": WorkflowTechnique.CONTENT_GENERATION,
    "ai": WorkflowTechnique.CONTENT_GENERATION,
    "artificial intelligence": WorkflowTechnique.CONTENT_GENERATION,
    "gpt": WorkflowTechnique.CONTENT_GENERATION,
    "chatgpt": WorkflowTechnique.CONTENT_GENERATION,
    "llm": WorkflowTechnique.CONTENT_GENERATION,
    "language model": WorkflowTechnique.CONTENT_GENERATION,
    "content creation": WorkflowTechnique.CONTENT_GENERATION,
    "content generation": WorkflowTechnique.CONTENT_GENERATION,
    "creative content": WorkflowTechnique.CONTENT_GENERATION,
    "natural language generation": WorkflowTechnique.CONTENT_GENERATION,
    "nlp": WorkflowTechnique.CONTENT_GENERATION,
    "text creation": WorkflowTechnique.CONTENT_GENERATION,
    "video generation": WorkflowTechnique.CONTENT_GENERATION,
    "audio generation": WorkflowTechnique.CONTENT_GENERATION,
    "write": WorkflowTechnique.CONTENT_GENERATION,
    "writing": WorkflowTechnique.CONTENT_GENERATION,
    "create": WorkflowTechnique.CONTENT_GENERATION,
    "generation": WorkflowTechnique.CONTENT_GENERATION,
    "creative": WorkflowTechnique.CONTENT_GENERATION,
    "compose": WorkflowTechnique.CONTENT_GENERATION,
    "compose": WorkflowTechnique.CONTENT_GENERATION,
    "story": WorkflowTechnique.CONTENT_GENERATION,
    "storytelling": WorkflowTechnique.CONTENT_GENERATION,
    "article": WorkflowTechnique.CONTENT_GENERATION,
    "blog": WorkflowTechnique.CONTENT_GENERATION,
    "caption": WorkflowTechnique.CONTENT_GENERATION,
    "headline": WorkflowTechnique.CONTENT_GENERATION,
    "summary": WorkflowTechnique.CONTENT_GENERATION,


    # Scraping / Research
    "news": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "weather": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "api": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "data collection": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "data gathering": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "scrape": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "scraping": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "research": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "fetch": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "retrieve": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "collect": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "gather": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "extract": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "crawl": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "crawling": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "spider": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "spidering": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "Content Retrieval": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "botting": WorkflowTechnique.SCRAPING_AND_RESEARCH,

    


    # Knowledge / CRM
    "crm": WorkflowTechnique.KNOWLEDGE_BASE,
    "customer data": WorkflowTechnique.KNOWLEDGE_BASE,
    "knowledge base": WorkflowTechnique.KNOWLEDGE_BASE,
    "knowledge management": WorkflowTechnique.KNOWLEDGE_BASE,
    "data store": WorkflowTechnique.KNOWLEDGE_BASE,
    "data storage": WorkflowTechnique.KNOWLEDGE_BASE,
    "vector store": WorkflowTechnique.KNOWLEDGE_BASE,
    "document store": WorkflowTechnique.KNOWLEDGE_BASE,
    "document management": WorkflowTechnique.KNOWLEDGE_BASE,
    "database": WorkflowTechnique.KNOWLEDGE_BASE,
    "knowledge graph": WorkflowTechnique.KNOWLEDGE_BASE,
    "customer relationship management": WorkflowTechnique.KNOWLEDGE_BASE,

    
}
# ....... 

# from backend.n8n_worflow.node_connection_types import NodeConnectionTypes
# from backend.mytypes.categorization import WorkflowTechnique
# from backend.n8n_worflow.node_connection_types import NodeConnectionTypes

# TECHNIQUE_TO_CONNECTION_MAP = {
#     WorkflowTechnique.CONTENT_GENERATION: NodeConnectionTypes.AiLanguageModel,
#     WorkflowTechnique.NOTIFICATION: NodeConnectionTypes.AiTool,
#     WorkflowTechnique.SCHEDULING: NodeConnectionTypes.Main,
#     WorkflowTechnique.SCRAPING_AND_RESEARCH: NodeConnectionTypes.Main,
#     WorkflowTechnique.KNOWLEDGE_BASE: NodeConnectionTypes.AiVectorStore,
#     WorkflowTechnique.KNOWLEDGE_BASE: NodeConnectionTypes.AiDocument,
#     WorkflowTechnique.CHATBOT: NodeConnectionTypes.AiLanguageModel,
# }

# #...

# def normalize_techniques(raw_techniques: List[str]) -> List[WorkflowTechnique]:
#     normalized = set()

#     for raw in raw_techniques:
#         raw_lower = raw.lower()

#         # 1️ Direct enum name match (IMPORTANT)
#         for technique in WorkflowTechnique:
#             if raw_lower == technique.value:
#                 normalized.add(technique)
#                 break
#         else:
#             # 2️ Keyword-based fallback
#             for keyword, enum_value in KEYWORD_TECHNIQUE_MAP.items():
#                 if keyword in raw_lower:
#                     normalized.add(enum_value)

#     return list(normalized)


def normalize_techniques(raw_techniques: List[str]) -> List[WorkflowTechnique]:
    normalized: set[WorkflowTechnique] = set()

    for raw in raw_techniques:
        text = raw.lower().strip()

        for technique in WorkflowTechnique:
            if text == technique.value:
                normalized.add(technique)
                break
        else:
            for keyword, technique in KEYWORD_TECHNIQUE_MAP.items():
                if keyword in text:
                    normalized.add(technique)

    return sorted(normalized, key=lambda t: t.value)
