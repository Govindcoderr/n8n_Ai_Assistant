from typing import List, Literal
from pydantic import BaseModel, Field
from langchain.schema import SystemMessage, HumanMessage
from langchain.chat_models.base import BaseChatModel

from .base import create_evaluator_chain, invoke_evaluator_chain
from ..evalution_chain.evalution import EvaluationInput

class Violation(BaseModel):
    type: Literal["critical", "major", "minor"]
    description: str
    pointsDeducted: float = Field(ge=0)


class NodeConfigurationResult(BaseModel):
    score: float = Field(ge=0, le=1)
    violations: List[Violation]
    analysis: str

SYSTEM_PROMPT = """
You are an expert n8n workflow evaluator focusing specifically on NODE CONFIGURATION and PARAMETERS.
Your task is to evaluate whether nodes are configured with correct parameters and settings.

## CRITICAL: Understanding n8n Credentials and Configuration
- NEVER penalize nodes for missing credentials
- Credentials are ALWAYS configured at runtime through the n8n UI
- Empty "credentials": {} fields are NORMAL and EXPECTED
- Focus on actual parameter misconfiguration, not missing credentials

## Valid Placeholder Patterns
DO NOT penalize:
- <UNKNOWN> values
- Empty strings ("")
- Empty resource selectors
- Placeholder API keys like "YOUR_API_KEY"

Empty string ("") and <UNKNOWN> are BOTH valid placeholders

## Special Tool Node Handling
- $fromAI expressions are VALID in ANY tool node
- {{ $fromAI('parameter', 'description') }} is correct and expected

## Evaluation Criteria

### Critical (-30 to -40):
- Incorrect implementation of user-provided values
- Required parameters completely missing
- Runtime crash configurations
- NEVER penalize missing credentials

### Major (-10 to -20):
- Wrong operation mode
- Missing operation/resource selection

### Minor (-2 to -5):
- Suboptimal but working configs

## Scoring
1. Start from 100
2. Deduct points
3. Convert to 0–1 scale
"""
HUMAN_TEMPLATE = """
Evaluate the node configuration of this workflow:

<user_prompt>
{userPrompt}
</user_prompt>

<generated_workflow>
{generatedWorkflow}
</generated_workflow>

{referenceSection}

Provide a node configuration evaluation with score, violations, and brief analysis.
"""
def create_node_configuration_evaluator_chain(llm: BaseChatModel):
    return create_evaluator_chain(
        llm=llm,
        result_model=NodeConfigurationResult,
        system_prompt=SYSTEM_PROMPT,
        human_template=HUMAN_TEMPLATE,
    )

def evaluate_node_configuration(
    llm: BaseChatModel,
    input: EvaluationInput,
) -> NodeConfigurationResult:
    chain = create_node_configuration_evaluator_chain(llm)
    return invoke_evaluator_chain(chain, input)

