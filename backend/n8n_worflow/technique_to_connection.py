from backend.mytypes.categorization import WorkflowTechnique
from backend.n8n_worflow.node_connection_types import NodeConnectionTypes


TECHNIQUE_TO_CONNECTION_MAP: dict[WorkflowTechnique, list[str]] = {
    WorkflowTechnique.CONTENT_GENERATION: [
        NodeConnectionTypes.AiLanguageModel
    ],
    WorkflowTechnique.NOTIFICATION: [
        NodeConnectionTypes.Action
    ],
    WorkflowTechnique.SCHEDULING: [
        NodeConnectionTypes.Trigger,
        NodeConnectionTypes.Main
    ],
    WorkflowTechnique.SCRAPING_AND_RESEARCH: [
        NodeConnectionTypes.Main
    ],
    WorkflowTechnique.KNOWLEDGE_BASE: [
        NodeConnectionTypes.AiVectorStore,
        NodeConnectionTypes.AiDocument
    ],
    WorkflowTechnique.CHATBOT: [
        NodeConnectionTypes.AiLanguageModel,
        NodeConnectionTypes.AiTool
    ],
    
}
