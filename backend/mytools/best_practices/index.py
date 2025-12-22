from typing import Dict, Optional

from backend.mytypes.categorization import WorkflowTechnique, WorkflowTechniqueType
from backend.mytypes.best_practice import BestPracticesDocument

from backend.mytools.best_practices.chatbot import ChatbotBestPractices
from backend.mytools.best_practices.content_generation import ContentGenerationBestPractices
from backend.mytools.best_practices.data_analysis import DataAnalysisBestPractices
from backend.mytools.best_practices.data_extraction import DataExtractionBestPractices
from backend.mytools.best_practices.data_transformation import DataTransformationBestPractices
from backend.mytools.best_practices.document_processing import DocumentProcessingBestPractices
from backend.mytools.best_practices.enrichment import EnrichmentBestPractices
from backend.mytools.best_practices.form_input import FormInputBestPractices
from backend.mytools.best_practices.human_in_the_loop import HumanInTheLoopBestPractices
from backend.mytools.best_practices.knowledge_base import KnowledgeBaseBestPractices
from backend.mytools.best_practices.monitoring import MonitoringBestPractices
from backend.mytools.best_practices.notification import NotificationBestPractices
from backend.mytools.best_practices.scraping_and_research import ScrapingAndResearchBestPractices
from backend.mytools.best_practices.scheduling import SchedulingBestPractices
from backend.mytools.best_practices.triage import TriageBestPractices


# Exact equivalent of:
# Record<WorkflowTechniqueType, BestPracticesDocument | undefined>

documentation: Dict[
    WorkflowTechniqueType,
    Optional[BestPracticesDocument]
] = {
    WorkflowTechnique.SCRAPING_AND_RESEARCH: ScrapingAndResearchBestPractices(),
    WorkflowTechnique.CHATBOT: ChatbotBestPractices(),
    WorkflowTechnique.CONTENT_GENERATION: ContentGenerationBestPractices(),
    WorkflowTechnique.DATA_ANALYSIS: DataAnalysisBestPractices(),
    WorkflowTechnique.DATA_EXTRACTION: DataExtractionBestPractices(),
    WorkflowTechnique.DATA_TRANSFORMATION: DataTransformationBestPractices(),
    WorkflowTechnique.DOCUMENT_PROCESSING: DocumentProcessingBestPractices(),
    WorkflowTechnique.ENRICHMENT: EnrichmentBestPractices(),
    WorkflowTechnique.FORM_INPUT: FormInputBestPractices(),
    WorkflowTechnique.KNOWLEDGE_BASE: KnowledgeBaseBestPractices(),
    WorkflowTechnique.NOTIFICATION: NotificationBestPractices(),
    WorkflowTechnique.TRIAGE: TriageBestPractices(),
    WorkflowTechnique.HUMAN_IN_THE_LOOP: HumanInTheLoopBestPractices(),
    WorkflowTechnique.MONITORING: MonitoringBestPractices(),
    WorkflowTechnique.SCHEDULING: SchedulingBestPractices()
}

