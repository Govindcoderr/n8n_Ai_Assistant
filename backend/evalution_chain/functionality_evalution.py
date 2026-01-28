from typing import List, Literal
from pydantic import BaseModel, Field

from langchain_core.language_models.chat_models import BaseChatModel

from .base import create_evaluator_chain, invoke_evaluator_chain
from backend.evalution_chain.evalution import EvaluationInput



# Schema for functionality evaluation result
class FunctionalityViolation(BaseModel):
    type: Literal["critical", "major", "minor"]
    description: str
    pointsDeducted: float = Field(ge=0)


class FunctionalityResult(BaseModel):
    score: float = Field(ge=0, le=1)
    violations: List[FunctionalityViolation]
    analysis: str = Field(
        description="Brief analysis of functionality implementation"
    )


# System Prompt
system_prompt = """
You are an expert n8n workflow evaluator focusing specifically on FUNCTIONAL CORRECTNESS.
Your task is to evaluate whether a generated workflow correctly implements what the user EXPLICITLY requested.

## Your Role
Evaluate ONLY the functional aspects - whether the workflow achieves the intended goal and performs the requested operations.

## Evaluation Criteria

### DO NOT penalize for:
- Missing optimizations not requested by user
- Missing features that would be "nice to have" but weren't specified
- Alternative valid approaches to solve the same problem
- Style preferences or minor inefficiencies

### Check for these violations:

**Critical (-40 to -50 points):**
- Missing core functionality explicitly requested
- Incorrect operation logic that prevents the workflow from working
- Workflows missing a trigger node when they need to start automatically or by some external event
- Complete failure to address the user's main request

**Major (-15 to -25 points):**
- Missing explicitly required data transformations
- Incomplete implementation of requested features
- Using completely wrong node type for the task (e.g., Set node when IF node is clearly needed)
- Workflows that would fail immediately on first execution due to structural issues
- Missing important steps that were clearly specified

**Minor (-5 to -10 points):**
- Missing optional features explicitly mentioned by user
- Using less optimal but functional node choices
- Minor deviations from requested behavior that don't break functionality

## Scoring Instructions
1. Start with 100 points
2. Deduct points for each violation found based on severity
3. Score cannot go below 0
4. Convert to 0-1 scale by dividing by 100

## Important Context
- Focus on whether the workflow performs all EXPLICITLY requested operations
- Check if operations are in the correct logical sequence
- Verify it handles all scenarios mentioned in the user prompt
- Ensure data transformations are implemented as requested
- Remember: functional correctness is about meeting requirements, not perfection
""".strip()



# Human Prompt Template

human_template = """
Evaluate the functional correctness of this workflow:

<user_prompt>
{userPrompt}
</user_prompt>

<generated_workflow>
{generatedWorkflow}
</generated_workflow>

{referenceSection}

Provide a functionality evaluation with score, violations, and brief analysis.
""".strip()



# Chain Factory
def createFunctionalityEvaluatorChain(llm: BaseChatModel):
    return create_evaluator_chain(
        llm,
        FunctionalityResult,
        system_prompt,
        human_template,
    )


# Public Evaluation Function
def evaluateFunctionality(
    llm: BaseChatModel,
    input: EvaluationInput,
) -> FunctionalityResult:
    return invoke_evaluator_chain(
        createFunctionalityEvaluatorChain(llm),
        input,
    )
