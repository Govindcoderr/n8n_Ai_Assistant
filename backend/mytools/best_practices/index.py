from typing import Dict, Optional

from mytypes.categorization import WorkflowTechnique, WorkflowTechniqueType
from mytypes import BestPracticesDocument

from backend.mytools.best_practices.chatbot import ChatbotBestPractices
from backend.mytools.best_practices import ContentGenerationBestPractices
# from .data_analysis import DataAnalysisBestPractices
from backend.mytools.best_practices.data_extraction import DataExtractionBestPractices
from backend.mytools.best_practices.data_transformation import DataTransformationBestPractices
from backend.mytools.best_practices.document_processing import DocumentProcessingBestPractices
# from .enrichment import EnrichmentBestPractices
from backend.mytools.best_practices.form_input import FormInputBestPractices
# from .human_in_the_loop import HumanInTheLoopBestPractices
# from .knowledge_base import KnowledgeBaseBestPractices
# from .monitoring import MonitoringBestPractices
# from .notification import NotificationBestPractices
from backend.mytools.best_practices.scraping_and_research import ScrapingAndResearchBestPractices
# from .scheduling import SchedulingBestPractices
# from .triage import TriageBestPractices


# Exact equivalent of:
# Record<WorkflowTechniqueType, BestPracticesDocument | undefined>

documentation: Dict[
    WorkflowTechniqueType,
    Optional[BestPracticesDocument]
] = {
    WorkflowTechnique.SCRAPING_AND_RESEARCH: ScrapingAndResearchBestPractices(),
    WorkflowTechnique.CHATBOT: ChatbotBestPractices(),
    WorkflowTechnique.CONTENT_GENERATION: ContentGenerationBestPractices(),
    WorkflowTechnique.DATA_ANALYSIS: None,  # DataAnalysisBestPractices()
    WorkflowTechnique.DATA_EXTRACTION: DataExtractionBestPractices(),
    WorkflowTechnique.DATA_TRANSFORMATION: DataTransformationBestPractices(),
    WorkflowTechnique.DOCUMENT_PROCESSING: DocumentProcessingBestPractices(),
    WorkflowTechnique.ENRICHMENT: None,  # EnrichmentBestPractices()
    WorkflowTechnique.FORM_INPUT: FormInputBestPractices(),
    WorkflowTechnique.KNOWLEDGE_BASE: None,  # KnowledgeBaseBestPractices()
    WorkflowTechnique.NOTIFICATION: None,  # NotificationBestPractices()
    WorkflowTechnique.TRIAGE: None,  # TriageBestPractices()
    WorkflowTechnique.HUMAN_IN_THE_LOOP: None,  # HumanInTheLoopBestPractices()
    WorkflowTechnique.MONITORING: None,  # MonitoringBestPractices()
    WorkflowTechnique.SCHEDULING: None,  # SchedulingBestPractices()
}

