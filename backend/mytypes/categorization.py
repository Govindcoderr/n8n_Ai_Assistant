from typing import List, Optional
from typing_extensions import Literal, TypedDict
from dataclasses import dataclass

WorkflowTechnique = Literal[
    "scheduling",
    "chatbot",
    "form_input",
    "scraping_and_research",
    "monitoring",
    "enrichment",
    "triage",
    "content_generation",
    "document_processing",
    "data_extraction",
    "data_analysis",
    "data_transformation",
    "notification",
    "knowledge_base",
    "human_in_the_loop",
]

TechniqueDescription = {
    "scheduling": "Running an action at a specific time or interval",
    "chatbot": "Receiving chat messages and replying",
    "form_input": "Gathering data from users via forms",
    "scraping_and_research": "Collecting information from websites or APIs",
    "monitoring": "Checking service or website status repeatedly",
    "enrichment": "Adding extra details from other sources",
    "triage": "Classifying data for routing or prioritization",
    "content_generation": "Creating text, images, audio, or video",
    "document_processing": "Taking action on content within files",
    "data_extraction": "Pulling specific information from inputs",
    "data_analysis": "Finding patterns or insights in data",
    "data_transformation": "Cleaning or restructuring data",
    "notification": "Sending alerts or updates",
    "knowledge_base": "Building or using a centralized knowledge store",
    "human_in_the_loop": "Pausing for human input",
}


# class PromptCategorization(TypedDict):
#     techniques: List[WorkflowTechnique]
#     confidence: Optional[float]

@dataclass
class PromptCategorization:
    techniques: List[str]
    confidence: Optional[float] = None