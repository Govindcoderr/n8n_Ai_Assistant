from pydantic import BaseModel, Field
from typing import Dict, Any

from backend.Chains.prompt_categorization import prompt_categorization_chain
from backend.error import ValidationError, ToolExecutionError
from backend.mytools.helpers.progress  import create_progress_reporter
from backend.mytools.helpers.response import (
    create_success_response,
    create_error_response,

)
from backend.mytypes.tools import CategorizePromptOutput

class CategorizePromptSchema(BaseModel):
    prompt: str = Field(..., min_length=1, description="The user prompt to categorize")


CATEGORIZE_PROMPT_TOOL = {
    "tool_name": "categorize_prompt",
    "display_title": "Categorizing prompt",
}


def build_categorization_message(categorization) -> str:
    parts = ["Prompt categorized"]

    if categorization.techniques:
        parts.append(f"- Techniques: {', '.join(categorization.techniques)}")

    if categorization.confidence is not None:
        parts.append(f"- Confidence: {int(categorization.confidence * 100)}%")

    return "\n".join(parts)


def create_categorize_prompt_tool(llm):
    def tool(input_data: Dict[str, Any]):
        reporter = create_progress_reporter(
            CATEGORIZE_PROMPT_TOOL["tool_name"],
            CATEGORIZE_PROMPT_TOOL["display_title"],
        )

        try:
            validated = CategorizePromptSchema(**input_data)
            reporter.start(validated.dict())

            reporter.progress("Analyzing prompt to identify use case and techniques...")
            categorization = prompt_categorization_chain(llm, validated.prompt)

            output = CategorizePromptOutput(categorization=categorization)
            reporter.complete(output)

            return create_success_response(
                build_categorization_message(categorization),
                {
                    "categorization": categorization.__dict__,
                    "techniqueCategories": categorization.techniques,
                },
            )

        except ValidationError as e:
            reporter.error(e)
            return create_error_response(e)

        except Exception as e:
            tool_error = ToolExecutionError(
                str(e),
                tool_name=CATEGORIZE_PROMPT_TOOL["tool_name"],
                cause=e,
            )
            reporter.error(tool_error)
            return create_error_response(tool_error)

    return tool
