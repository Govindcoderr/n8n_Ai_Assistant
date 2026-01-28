
from typing import List, Dict, Any ,Optional, Literal
from pydantic import BaseModel, Field, confloat
from langchain_core.language_models.chat_models import BaseChatModel

# External Imports (SAME ROLE AS TS)

from backend.mytools.best_practices.index import documentation
from backend.evalution_chain.base import create_evaluator_chain
from backend.evalution_chain.evalution import EvaluationInput
from backend.Chains.prompt_categorization  import prompt_categorization_chain

# Schema (ZOD → PYDANTIC)
class BestPracticeViolation(BaseModel):
    type: Literal["major", "minor"]
    description: str
    pointsDeducted: float = Field(ge=0)


class BestPracticesResult(BaseModel):
    score: float = Field(..., ge=0, le=1)
    violations: List[BestPracticeViolation]
    techniques: List[str] = Field(
        ...,
        description=(
            "Workflow techniques identified for this evaluation "
            "(e.g., chatbot, content-generation)"
        ),
    )



# SYSTEM PROMPT (UNCHANGED)
system_prompt = """You are an expert n8n workflow evaluator focusing specifically on BEST PRACTICES ADHERENCE.
Your task is to evaluate whether a generated workflow follows the documented best practices for its workflow type(s).

## Your Role
Evaluate ONLY adherence to the provided best practices documentation. Focus on whether the workflow follows recommended patterns, avoids common pitfalls, and uses nodes correctly.

## Context-Aware Evaluation Philosophy

CRITICAL: Always consider what the user actually requested in their prompt. Do not penalize workflows for missing features or safeguards that were not part of the user's requirements.

- If the user asked for a simple workflow without mentioning production readiness, error handling, or rate limiting, these should NOT be critical violations
- Only mark something as critical if it would prevent the workflow from fulfilling the user's specific request
- Consider the scope and complexity implied by the user's prompt

## Evaluation Criteria

n8n workflows can have multiple triggers and execution paths. Before marking components as disconnected,
check ALL possible connection methods including AI memory, tools, vector stores, shared storage, and agents.

DO NOT penalize for missing best practices that are not relevant to what the user asked for.
DO NOT create arbitrary best practices.
DO NOT mark optional features as critical when they were not requested.
"""



# HUMAN PROMPT TEMPLATE
human_template = """Evaluate how well this workflow follows n8n best practices in the context of what the user requested.

<user_prompt>
{userPrompt}
</user_prompt>

<generated_workflow>
{generatedWorkflow}
</generated_workflow>

<best_practices_documentation>
{bestPractices}
</best_practices_documentation>

{referenceSection}

IMPORTANT:
- First analyze what the user actually requested
- Only evaluate best practices relevant to that request
- Do NOT mark missing optional features as critical
"""



# EVALUATOR CHAIN CREATOR
def createBestPracticesEvaluatorChain(llm: BaseChatModel):
    return create_evaluator_chain(
        llm=llm,
        result_model=BestPracticesResult,
        system_prompt=system_prompt,
        human_template=human_template,
    )


# LOAD RELEVANT BEST PRACTICES
def loadRelevantBestPractices(
    llm: BaseChatModel,
    userPrompt: str,
) -> Dict[str, Any]:
    try:
        # Categorize user prompt
        categorization =  prompt_categorization_chain(llm, userPrompt)

        relevant_docs: List[str] = []

        for technique in categorization.get("techniques", []):
            best_practice = documentation.get(technique)
            if best_practice:
                relevant_docs.append(
                    f"## Best Practices for {technique}\n\n"
                    f"{best_practice.get_documentation()}"
                )

        if not relevant_docs:
            return {
                "documentation": (
                    "No specific best practices documentation available for this workflow type. "
                    "Evaluate based on general n8n workflow principles."
                ),
                "techniques": categorization.get("techniques", []),
            }

        return {
            "documentation": "\n\n---\n\n".join(relevant_docs),
            "techniques": categorization.get("techniques", []),
        }

    except Exception:
        return {
            "documentation": (
                "Unable to load specific best practices. "
                "Evaluate based on general n8n workflow principles."
            ),
            "techniques": [],
        }


# MAIN EVALUATION FUNCTION
def evaluateBestPractices(
    llm: BaseChatModel,
    input: EvaluationInput,
) -> BestPracticesResult:
    # Load best practices + techniques
    best_practices_data = loadRelevantBestPractices(
        llm,
        input.userPrompt,
    )

    # Optional reference workflow
    referenceSection = (
        f"<reference_workflow>\n{input.referenceWorkflow}\n</reference_workflow>"
        if input.referenceWorkflow
        else ""
    )

    # Create evaluator chain
    chain = createBestPracticesEvaluatorChain(llm)

    chain_input = {
        "userPrompt": input.userPrompt,
        "generatedWorkflow": input.generatedWorkflow,
        "bestPractices": best_practices_data["documentation"],
        "referenceSection": referenceSection,
    }

    # Invoke evaluator
    result = chain.invoke(chain_input)

    # Attach techniques and return
    return BestPracticesResult(
        **result,
        # techniques=best_practices_data["techniques"],
    )
