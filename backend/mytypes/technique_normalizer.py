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

    # Notification / Messaging
    "message": WorkflowTechnique.NOTIFICATION,
    "messaging": WorkflowTechnique.NOTIFICATION,
    "whatsapp": WorkflowTechnique.NOTIFICATION,
    "sms": WorkflowTechnique.NOTIFICATION,
    "email": WorkflowTechnique.NOTIFICATION,
    "instagram": WorkflowTechnique.NOTIFICATION,

    # Content Generation
    "image generation": WorkflowTechnique.CONTENT_GENERATION,
    "generate image": WorkflowTechnique.CONTENT_GENERATION,
    "text generation": WorkflowTechnique.CONTENT_GENERATION,
    "ai": WorkflowTechnique.CONTENT_GENERATION,

    # Scraping / Research
    "news": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "weather": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "api": WorkflowTechnique.SCRAPING_AND_RESEARCH,
    "data collection": WorkflowTechnique.SCRAPING_AND_RESEARCH,

    # Knowledge / CRM
    "crm": WorkflowTechnique.KNOWLEDGE_BASE,
    "customer data": WorkflowTechnique.KNOWLEDGE_BASE,
}


def normalize_techniques(raw_techniques: List[str]) -> List[WorkflowTechnique]:
    normalized = set()

    for raw in raw_techniques:
        raw_lower = raw.lower()

        for keyword, enum_value in KEYWORD_TECHNIQUE_MAP.items():
            if keyword in raw_lower:
                normalized.add(enum_value)

    return list(normalized)

