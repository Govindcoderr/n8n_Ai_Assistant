# from typing import List, Optional
# from typing_extensions import Literal, TypedDict
# from dataclasses import dataclass

# WorkflowTechnique = Literal[
#     "scheduling",
#     "chatbot",
#     "form_input",
#     "scraping_and_research",
#     "monitoring",
#     "enrichment",
#     "triage",
#     "content_generation",
#     "document_processing",
#     "data_extraction",
#     "data_analysis",
#     "data_transformation",
#     "notification",
#     "knowledge_base",
#     "human_in_the_loop",
# ]

# TechniqueDescription = {
#     "scheduling": "Running an action at a specific time or interval",
#     "chatbot": "Receiving chat messages and replying",
#     "form_input": "Gathering data from users via forms",
#     "scraping_and_research": "Collecting information from websites or APIs",
#     "monitoring": "Checking service or website status repeatedly",
#     "enrichment": "Adding extra details from other sources",
#     "triage": "Classifying data for routing or prioritization",
#     "content_generation": "Creating text, images, audio, or video",
#     "document_processing": "Taking action on content within files",
#     "data_extraction": "Pulling specific information from inputs",
#     "data_analysis": "Finding patterns or insights in data",
#     "data_transformation": "Cleaning or restructuring data",
#     "notification": "Sending alerts or updates",
#     "knowledge_base": "Building or using a centralized knowledge store",
#     "human_in_the_loop": "Pausing for human input",
# }


# # class PromptCategorization(TypedDict):
# #     techniques: List[WorkflowTechnique]
# #     confidence: Optional[float]

# @dataclass
# class PromptCategorization:
#     techniques: List[str]
#     confidence: Optional[float] = None





from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass

class WorkflowTechnique(str, Enum):
    """Common workflow building techniques that can be combined in workflows"""

    SCHEDULING = "scheduling"
    CHATBOT = "chatbot"
    FORM_INPUT = "form_input"
    SCRAPING_AND_RESEARCH = "scraping_and_research"
    MONITORING = "monitoring"
    ENRICHMENT = "enrichment"
    TRIAGE = "triage"
    CONTENT_GENERATION = "content_generation"
    DOCUMENT_PROCESSING = "document_processing"
    DATA_EXTRACTION = "data_extraction"
    DATA_ANALYSIS = "data_analysis"
    DATA_TRANSFORMATION = "data_transformation"
    NOTIFICATION = "notification"
    KNOWLEDGE_BASE = "knowledge_base"
    HUMAN_IN_THE_LOOP = "human_in_the_loop"

WorkflowTechniqueType = WorkflowTechnique

TechniqueDescription: Dict[WorkflowTechniqueType, str] = {
    WorkflowTechnique.SCHEDULING:
        "Running an action at a specific time or interval",

    WorkflowTechnique.CHATBOT:
        "Receiving chat messages and replying (built-in chat, Telegram, Slack, MS Teams, etc.)",

    WorkflowTechnique.FORM_INPUT:
        "Gathering data from users via forms",

    WorkflowTechnique.SCRAPING_AND_RESEARCH:
        "Methodically collecting information from websites or APIs to compile structured data",

    WorkflowTechnique.MONITORING:
        "Repeatedly checking service/website status and taking action when conditions are met",

    WorkflowTechnique.ENRICHMENT:
        "Adding extra details to existing data by merging information from other sources",

    WorkflowTechnique.TRIAGE:
        "Classifying data for routing or prioritization",

    WorkflowTechnique.CONTENT_GENERATION:
        "Creating text, images, audio, video, etc.",

    WorkflowTechnique.DOCUMENT_PROCESSING:
        "Taking action on content within files (PDFs, Word docs, images)",

    WorkflowTechnique.DATA_EXTRACTION:
        "Pulling specific information from structured or unstructured inputs",

    WorkflowTechnique.DATA_ANALYSIS:
        "Examining data to find patterns, trends, anomalies, or insights",

    WorkflowTechnique.DATA_TRANSFORMATION:
        "Cleaning, formatting, or restructuring data (including summarization)",

    WorkflowTechnique.NOTIFICATION:
        "Sending alerts or updates via email, chat, SMS when events occur",

    WorkflowTechnique.KNOWLEDGE_BASE:
        "Building or using a centralized information collection (usually vector database for LLM use)",

    WorkflowTechnique.HUMAN_IN_THE_LOOP:
        "Pausing for human decision/input before resuming",
}

@dataclass
class PromptCategorization:
    """
    Result of prompt categorization
    """

    techniques: List[WorkflowTechniqueType]
    confidence: Optional[float] = None
