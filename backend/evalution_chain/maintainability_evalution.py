from typing import List, Literal
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel

from .base import create_evaluator_chain, invoke_evaluator_chain
from backend.evalution_chain.evalution import EvaluationInput


# ---------- SCHEMA ----------

class MaintainabilityViolation(BaseModel):
    type: Literal["critical", "major", "minor"]
    description: str
    pointsDeducted: float = Field(ge=0)


class MaintainabilityResult(BaseModel):
    score: float = Field(ge=0, le=1)
    violations: List[MaintainabilityViolation]

    nodeNamingQuality: float = Field(
        ge=0, le=1, description="Score for descriptive node naming"
    )
    workflowOrganization: float = Field(
        ge=0, le=1, description="Score for logical workflow structure"
    )
    modularity: float = Field(
        ge=0, le=1, description="Score for reusable and modular components"
    )

    analysis: str = Field(
        description="Brief analysis of workflow maintainability"
    )


# ---------- SYSTEM PROMPT ----------

system_prompt = """
You are an expert n8n workflow evaluator focusing specifically on WORKFLOW MAINTAINABILITY.
Your task is to evaluate how maintainable and well-organized the workflow is.

## Maintainability Metrics
1. Node Naming Quality (0-1)
2. Workflow Organization (0-1)
3. Modularity (0-1)

Overall score = average of the three metrics.

Focus on clarity, structure, and reusability.
""".strip()


# ---------- HUMAN TEMPLATE ----------

human_template = """
Evaluate the maintainability of this workflow:

<user_prompt>
{userPrompt}
</user_prompt>

<generated_workflow>
{generatedWorkflow}
</generated_workflow>

{referenceSection}

Provide a maintainability evaluation with naming, organization, and modularity scores, violations, and analysis.
""".strip()


# ---------- CHAIN FACTORY ----------

def createMaintainabilityEvaluatorChain(llm: BaseChatModel):
    return create_evaluator_chain(
        llm,
        MaintainabilityResult,
        system_prompt,
        human_template,
    )


# ---------- PUBLIC EVALUATION FUNCTION ----------

def evaluateMaintainability(
    llm: BaseChatModel,
    input: EvaluationInput,
) -> MaintainabilityResult:

    raw_result = invoke_evaluator_chain(
        createMaintainabilityEvaluatorChain(llm),
        input,
    )

    #  dict → Pydantic model (VERY IMPORTANT)
    result = MaintainabilityResult(**raw_result)

    # same logic as TS: average of 3 metrics
    result.score = (
        result.nodeNamingQuality
        + result.workflowOrganization
        + result.modularity
    ) / 3

    return result
