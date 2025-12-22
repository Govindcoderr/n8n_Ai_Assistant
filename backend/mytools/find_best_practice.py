


from langchain.tools import BaseTool
from pydantic import BaseModel, validator, ValidationError as PydanticValidationError
from typing import List

from backend.error import ValidationError, ToolExecutionError
from backend.mytools.best_practices.index import documentation
from backend.mytools.helpers.progress import create_progress_reporter
from backend.mytools.helpers.response import create_success_response, create_error_response
from backend.mytypes.categorization import WorkflowTechnique
from backend.utills.stream_processor import BuilderToolBase

# Input Schema (Pydantic)

class GetBestPracticesInput(BaseModel):
    techniques: List[WorkflowTechnique]

    @validator("techniques")
    def validate_techniques(cls, v):
        if not v or len(v) == 0:
            raise ValueError("At least one technique is required.")
        return v


# Helper Function: format documentation

def format_best_practices(techniques: List[WorkflowTechnique]) -> str:
    parts = []
    found_docs = []

    for technique in techniques:
        doc = documentation.get(technique)
        if doc:
            found_docs.append(doc.get_documentation())

    if found_docs:
        parts.append("<best_practices>")
        parts.append("\n---\n".join(found_docs))
        parts.append("</best_practices>")

    return "\n".join(parts)

# Tool Metadata

GET_BEST_PRACTICES_TOOL: BuilderToolBase = {
    "toolName": "get_best_practices",
    "displayTitle": "Getting best practices",
}

# Main Tool Implementation

class GetBestPracticesTool(BaseTool):
    name = GET_BEST_PRACTICES_TOOL["toolName"]
    description = """
Retrieve best practices documentation for specific workflow techniques.

Use this tool after categorizing a user's prompt to get relevant guidance on:
- Recommended nodes and their purposes
- Common pitfalls to avoid
- Performance and resource management tips
- Implementation patterns and best practices
- General workflow guidance
"""

    args_schema = GetBestPracticesInput

    def _run(self, techniques: List[WorkflowTechnique], config=None):
        reporter = create_progress_reporter(
             config,
            GET_BEST_PRACTICES_TOOL["toolName"],
            # GET_BEST_PRACTICES_TOOL["displayTitle"],
        )

        try:
            # Validate input again (same behavior as n8n)
            validated = GetBestPracticesInput(techniques=techniques)
            techniques = validated.techniques

            reporter.start({"techniques": techniques})
            reporter.progress(f"Retrieving best practices for {len(techniques)} technique(s)...")

            # Filter which docs exist
            available_docs = [t for t in techniques if documentation.get(t)]

            if not available_docs:
                msg = (
                    "No best practices documentation available for the requested techniques: "
                    + ", ".join([str(t) for t in techniques])
                )
                reporter.complete({"techniques": techniques, "found": 0})
                return create_success_response(config, msg)

            # Format documentation
            message = format_best_practices(techniques)

            reporter.complete({
                "techniques": techniques,
                "found": len(available_docs),
                "missing": len(techniques) - len(available_docs),
            })

            return create_success_response(config, message)

        except PydanticValidationError as e:
            # Validation error (same as zod)
            validation_error = ValidationError("Invalid input parameters", extra={"errors": e.errors()})
            reporter.error(validation_error)
            return create_error_response(config, validation_error)

        except Exception as e:
            # General tool error
            tool_error = ToolExecutionError(
                str(e),
                toolName=GET_BEST_PRACTICES_TOOL["toolName"],
                cause=e,
            )
            reporter.error(tool_error)
            return create_error_response(config, tool_error)

# Factory Function (same pattern)

def create_get_best_practices_tool():
    return {
        "tool": GetBestPracticesTool(),
        **GET_BEST_PRACTICES_TOOL
    }
