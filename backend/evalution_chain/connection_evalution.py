from typing import List, Literal
from pydantic import BaseModel, Field

from langchain_core.language_models.chat_models import BaseChatModel

from backend.evalution_chain.base import create_evaluator_chain, invoke_evaluator_chain
from backend.evalution_chain.evalution import EvaluationInput


# Schema for connections evaluation result
class ConnectionViolation(BaseModel):
    type: Literal["critical", "major", "minor"]
    description: str
    pointsDeducted: float = Field(ge=0)


class ConnectionsResult(BaseModel):
    score: float = Field(ge=0, le=1)
    violations: List[ConnectionViolation]
    analysis: str = Field(
        description="Brief analysis of node connections and data flow"
    )



# System Prompt

system_prompt = """
You are an expert n8n workflow evaluator focusing specifically on NODE CONNECTIONS and DATA FLOW.
Your task is to verify that every connection follows n8n's sourcing rules, supports the requested behaviour, and respects hybrid AI patterns.

## Connection Model Overview

### 1. Main Workflow Connections
- Carry run-time data between workflow nodes (`main`)
- Flow from the node that PRODUCES data → node that CONSUMES data
- Required to keep the primary execution path intact (trigger → processing → outputs)

### 2. AI Capability Connections (`ai_*`)
- Sub-nodes PROVIDE capabilities and must be the source of the ai_* link
- Always point from sub-node → parent node
- Never replace the main data path; they augment the parent node

### 3. Hybrid Nodes
- May appear on both main and ai_* networks
- This is expected behaviour
- Only flag when a required connection is genuinely missing

### 4. Capability-Only Sub-nodes
- Document Loader, Token Splitter, Embeddings, LLMs, Tools, Memory, etc.
- Have NO main input/output by design
- NEVER penalize for missing main connections

### 5. Builder Knowledge
- ai_* links always originate from sub-nodes
- Memory and tools can connect to multiple parents
- Separate vector store nodes for insert vs retrieve are valid

## Scoring Rules
- Start at 100
- Deduct points per violation
- Convert final score to 0–1 scale

Focus on correctness of execution, direction of connections, and proper AI capability wiring.
""".strip()



# Human Prompt Template
human_template = """
Evaluate the connections and data flow of this workflow:

<user_prompt>
{userPrompt}
</user_prompt>

<generated_workflow>
{generatedWorkflow}
</generated_workflow>

{referenceSection}

Provide a connections evaluation with score, violations, and brief analysis.
""".strip()


# Chain Factory
def create_connections_evaluator_chain(llm: BaseChatModel):
    return create_evaluator_chain(
        llm=llm,
        result_model=ConnectionsResult,
        system_prompt=system_prompt,
        human_template=human_template,
    )



# Public Evaluation Function
def evaluate_connections(
    llm: BaseChatModel,
    input: EvaluationInput,
) -> ConnectionsResult:
    return invoke_evaluator_chain(
        create_connections_evaluator_chain(llm),
        input,
    )
