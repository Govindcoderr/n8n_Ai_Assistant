from typing import List, Literal
from pydantic import BaseModel, Field
from langchain_core.language_models.chat_models import BaseChatModel
from .base import create_evaluator_chain, invoke_evaluator_chain
from ..evalution_chain.evalution  import EvaluationInput

class Violation(BaseModel):
    type: Literal["critical", "major", "minor"]
    description: str
    pointsDeducted: float = Field(ge=0)


class EfficiencyResult(BaseModel):
    score: float = Field(ge=0, le=1)
    violations: List[Violation]
    redundancyScore: float = Field(
        ge=0, le=1, description="Score for avoiding redundant operations"
    )
    pathOptimization: float = Field(
        ge=0, le=1, description="Score for optimal execution paths"
    )
    nodeCountEfficiency: float = Field(
        ge=0, le=1, description="Score for using minimal nodes"
    )
    analysis: str = Field(description="Brief analysis of workflow efficiency")


system_prompt = """You are an expert n8n workflow evaluator focusing specifically on WORKFLOW EFFICIENCY.
Your task is to evaluate the efficiency of the workflow across three key metrics.

## CRITICAL: Understanding n8n Efficiency Patterns
- **AI agents with tools + separate nodes is NOT always duplication**
- **Backup/fallback paths are intentional redundancy for reliability**
- **Some redundancy improves maintainability**

## Efficiency Metrics

### 1. Redundancy Score (0-1)
- Check duplicate operations
- Avoid unnecessary transformations

### 2. Path Optimization (0-1)
- Optimal execution order
- Efficient branching

### 3. Node Count Efficiency (0-1)
- Minimal nodes for the task
- Avoid unnecessary intermediates

## Scoring Instructions
1. Calculate each metric score (0-1)
2. Identify violations
3. Overall score = average of the three metrics
4. Provide examples in analysis
"""
human_template = """Evaluate the efficiency of this workflow:

<user_prompt>
{userPrompt}
</user_prompt>

<generated_workflow>
{generatedWorkflow}
</generated_workflow>

{referenceSection}

Provide an efficiency evaluation with individual metric scores, overall score, violations, and analysis.
"""

# ---------- CHAIN ----------

def createEfficiencyEvaluatorChain(llm: BaseChatModel):
    return create_evaluator_chain(
        llm,
        EfficiencyResult,
        system_prompt,
        human_template,
    )

# ---------- EVALUATION (IMPORTANT PART) ----------

def evaluateEfficiency(
    llm: BaseChatModel,
    input: EvaluationInput,
) -> EfficiencyResult:

    raw_result =  invoke_evaluator_chain(
        createEfficiencyEvaluatorChain(llm),
        input,
    )

    #  raw_result IS dict — MUST convert
    efficiency = EfficiencyResult(**raw_result)

    # calculate overall score
    efficiency.score = (
        efficiency.redundancyScore
        + efficiency.pathOptimization
        + efficiency.nodeCountEfficiency
    ) / 3

    return efficiency