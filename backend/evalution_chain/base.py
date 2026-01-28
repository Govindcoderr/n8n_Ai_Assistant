from typing import Type, TypeVar, Dict, Any
from pydantic import BaseModel
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import Runnable, RunnableSequence


# Local Imports
from backend.evalution_chain.evalution import EvaluationInput

# Generic Result Type
TResult = TypeVar("TResult", bound=BaseModel)

# Custom Error (OperationalError equivalent)
class OperationalError(Exception):
    pass


# Evaluator Chain Creator
def create_evaluator_chain(
    llm: BaseChatModel,
    result_model: Type[TResult],
    system_prompt: str,
    human_template: str,
) -> RunnableSequence:
    """
    Python equivalent of createEvaluatorChain<T>
    """

    # Check if LLM supports structured output
    if not hasattr(llm, "with_structured_output"):
        raise OperationalError("LLM doesn't support structured output")

    # Build prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=system_prompt),
            HumanMessagePromptTemplate.from_template(human_template),
        ]
    )

    # Bind structured output
    llm_with_structured_output = llm.with_structured_output(result_model)

    # Create runnable sequence
    return RunnableSequence(
        prompt,
        llm_with_structured_output,
    )

# Invoke Evaluator Chain

def invoke_evaluator_chain(
    chain: Runnable,
    input: EvaluationInput,
) -> Any:
    """
    Python equivalent of invokeEvaluatorChain<T>
    """
    reference_section = (
        f"<reference_workflow>\n{input.referenceWorkflow}\n</reference_workflow>"
        if input.referenceWorkflow
        else ""
    )

    result =chain.invoke(
        {
            "userPrompt": input.userPrompt,
            "generatedWorkflow": input.generatedWorkflow,
            "referenceSection": reference_section,
        }
    )

    return result
