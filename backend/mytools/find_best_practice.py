#Yeh code ek LangChain tool banata hai jo categorized workflow techniques ke basis par best practices documentation fetch karke formatted response return karta hai, proper validation, progress tracking aur error handling ke saath.


from typing import List, Dict, Any

from langchain.tools import tool
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError

from  backend.error import ValidationError, ToolExecutionError
from  backend.mytools.best_practices import documentation
from  backend.mytools.helpers.progress import create_progress_reporter
from  backend.mytools.helpers.response import create_success_response, create_error_response
from  backend.mytypes.categorization import WorkflowTechnique, WorkflowTechniqueType
from  backend.utills.stream_processor import BuilderToolBase


class GetBestPracticesInput(BaseModel):
    techniques: List[WorkflowTechnique] = Field(
        ...,
        min_items=1,
        description="List of workflow techniques to retrieve best practices for",
    )

#  Format best practices documentation for multiple techniques

def format_best_practices(techniques: List[WorkflowTechniqueType]) -> str:
    parts: List[str] = []
    found_docs: List[str] = []

    for technique in techniques:
        doc = documentation.get(technique)
        if doc:
            found_docs.append(doc.get_documentation())

    if found_docs:
        parts.append("<best_practices>")
        parts.append("\n---\n".join(found_docs))
        parts.append("</best_practices>")

    return "\n".join(parts)


GET_BEST_PRACTICES_TOOL = BuilderToolBase(
    tool_name="get_best_practices",
    display_title="Getting best practices",
)

#  Factory function to create the get best practices tool

def create_get_best_practices_tool():
    @tool(
        name=GET_BEST_PRACTICES_TOOL.tool_name,
        description="""
Retrieve best practices documentation for specific workflow techniques.

Use this tool after categorizing a user's prompt to get relevant guidance on:
- Recommended nodes and their purposes
- Common pitfalls to avoid
- Performance and resource management tips
- Implementation patterns and best practices
- General tips on building workflows that utilise the provided techniques

This helps build better workflows by applying proven patterns and avoiding common mistakes.
""",
        args_schema=GetBestPracticesInput,
    )
    def get_best_practices(input: Dict[str, Any], config: Dict[str, Any]):
        reporter = create_progress_reporter(
            config,
            GET_BEST_PRACTICES_TOOL.tool_name,
            GET_BEST_PRACTICES_TOOL.display_title,
        )

        try:
            validated_input = GetBestPracticesInput(**input)
            techniques = validated_input.techniques

            reporter.start(validated_input.dict())
            reporter.progress(
                f"Retrieving best practices for {len(techniques)} technique(s)..."
            )

            available_docs = [
                t for t in techniques if t in documentation
            ]

            if not available_docs:
                message = (
                    "No best practices documentation available for the requested "
                    f"techniques: {', '.join(t.value for t in techniques)}"
                )
                reporter.complete({"techniques": techniques, "found": 0})
                return create_success_response(config, message)

            message = format_best_practices(techniques)

            reporter.complete(
                {
                    "techniques": techniques,
                    "found": len(available_docs),
                    "missing": len(techniques) - len(available_docs),
                }
            )

            return create_success_response(config, message)

        except PydanticValidationError as e:
            validation_error = ValidationError(
                "Invalid input parameters",
                extra={"errors": e.errors()},
            )
            reporter.error(validation_error)
            return create_error_response(config, validation_error)

        except Exception as e:
            tool_error = ToolExecutionError(
                str(e),
                tool_name=GET_BEST_PRACTICES_TOOL.tool_name,
                cause=e,
            )
            reporter.error(tool_error)
            return create_error_response(config, tool_error)

    return {
        "tool": get_best_practices,
        "toolName": GET_BEST_PRACTICES_TOOL.tool_name,
        "displayTitle": GET_BEST_PRACTICES_TOOL.display_title,
    }
