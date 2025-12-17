from dataclasses import dataclass
from typing import Any, Dict, Optional

from backend.mytypes.categorization import PromptCategorization


@dataclass
class CategorizePromptOutput:
    """
    Output contract for the categorize_prompt tool.

    This mirrors the structured response used by the tool layer and allows
    downstream systems (agents, UI, logging, orchestration engines) to rely
    on a stable schema.
    """

    categorization: PromptCategorization


@dataclass
class ToolResponse:
    """
    Generic tool response wrapper.

    Used to standardize responses across all tools in the system.
    """

    status: str
    message: str
    data: Optional[Dict[str, Any]] = None


@dataclass
class ToolErrorResponse:
    """
    Standard error response format for tool failures.
    """

    status: str
    message: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class BuilderToolMetadata:
    """
    Metadata describing a tool.

    This is useful for:
    - Tool registration
    - UI rendering
    - Logging and analytics
    """

    tool_name: str
    display_title: str
    description: Optional[str] = None
