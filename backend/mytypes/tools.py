# from dataclasses import dataclass
# from typing import Any, Dict, Optional

# from backend.mytypes.categorization import PromptCategorization


# @dataclass
# class CategorizePromptOutput:
#     """
#     Output contract for the categorize_prompt tool.

#     This mirrors the structured response used by the tool layer and allows
#     downstream systems (agents, UI, logging, orchestration engines) to rely
#     on a stable schema.
#     """

#     categorization: PromptCategorization


# @dataclass
# class ToolResponse:
#     """
#     Generic tool response wrapper.

#     Used to standardize responses across all tools in the system.
#     """

#     status: str
#     message: str
#     data: Optional[Dict[str, Any]] = None


# @dataclass
# class ToolErrorResponse:
#     """
#     Standard error response format for tool failures.
#     """

#     status: str
#     message: str
#     details: Optional[Dict[str, Any]] = None


# @dataclass
# class BuilderToolMetadata:
#     """
#     Metadata describing a tool.

#     This is useful for:
#     - Tool registration
#     - UI rendering
#     - Logging and analytics
#     """

#     tool_name: str
#     display_title: str
#     description: Optional[str] = None

# @dataclass
# class NodeSearchOutput:
#     """
#     Output contract for the node search tool.

#     This mirrors the structured response used by the tool layer and allows
#     downstream systems (agents, UI, logging, orchestration engines) to rely
#     on a stable schema.
#     """


from typing import Callable, TypedDict, List, Dict, Any, Optional, Literal, Union
from dataclasses import dataclass

from backend.mytypes.nodes import AddedNode, NodeDetails, NodeSearchResult
from backend.mytypes.categorization import PromptCategorization
# from backend.mytypes.workflow import SimpleWorkflow


# Progress update types

ProgressUpdateType = Literal["input", "output", "progress", "error"]


class ProgressUpdate(TypedDict, total=False):
    type: ProgressUpdateType
    data: Dict[str, Any]
    timestamp: Optional[str]


class ToolProgressMessage(TypedDict, total=False):
    type: Literal["tool"]
    toolName: str
    toolCallId: Optional[str]
    status: Literal["running", "completed", "error"]
    updates: List[ProgressUpdate]
    displayTitle: Optional[str]
    customDisplayTitle: Optional[str]


class ToolError(TypedDict, total=False):
    message: str
    code: Optional[str]
    details: Optional[Union[List[Any], Dict[str, Any]]]



# Progress reporter interfaces (protocol-style)
# @dataclass
# class ProgressReporter:
#     def start(self, input_data: Any, options: Optional[Dict[str, str]] = None) -> None:
#         ...

#     def progress(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
#         ...

#     def complete(self, output: Any) -> None:
#         ...

#     def error(self, error: ToolError) -> None:
#         ...

#     def create_batch_reporter(self, scope: str) -> "BatchReporter":
#         ...

@dataclass
class ProgressReporter:
    start: Callable[[Any], None]
    progress: Callable[[str, Optional[Dict[str, Any]]], None]
    complete: Callable[[Any], None]
    error: Callable[[Any], None]
    createBatchReporter: Callable[[str], Any]

# class BatchReporter:
#     def init(self, total: int) -> None:
#         ...

#     def next(self, item_description: str) -> None:
#         ...

#     def complete(self) -> None:
#         ...

class BatchReporter:
    def __init__(self, total: int) -> None:
        self.total = total
        self.current = 0

    def next(self, item_description: str) -> None:
        self.current += 1
        # emit progress here

    def complete(self) -> None:
        # mark batch completed
        pass

# Tool output types

class UpdateNodeParametersOutput(TypedDict):
    nodeId: str
    nodeName: str
    nodeType: str
    updatedParameters: Dict[str, Any]
    appliedChanges: List[str]
    message: str


class AddNodeOutput(TypedDict):
    addedNode: AddedNode
    message: str


class ConnectNodesOutput(TypedDict):
    sourceNode: str
    targetNode: str
    connectionType: str
    swapped: bool
    message: str
    found: Dict[str, bool]


class RemoveNodeOutput(TypedDict):
    removedNodeId: str
    removedNodeName: str
    removedNodeType: str
    connectionsRemoved: int
    message: str


class NodeDetailsOutput(TypedDict):
    details: NodeDetails
    found: bool
    message: str


class NodeSearchOutput(TypedDict):
    results: List[Dict[str, Any]]
    totalResults: int
    message: str


class GetNodeParameterOutput(TypedDict):
    message: str


class RemoveConnectionOutput(TypedDict):
    sourceNode: str
    targetNode: str
    connectionType: str
    sourceOutputIndex: int
    targetInputIndex: int
    message: str


class CategorizePromptOutput(TypedDict):
    categorization: PromptCategorization

# Workflow & configuration outputs

# class WorkflowMetadata(TypedDict, total=False):
#     name: str
#     description: Optional[str]
#     workflow: SimpleWorkflow


class NodeConfigurationEntry(TypedDict):
    version: int
    parameters: Dict[str, Any]


NodeConfigurationsMap = Dict[str, List[NodeConfigurationEntry]]

class GetWorkflowExamplesOutput(TypedDict):
    examples: List[Dict[str, str]]
    totalResults: int
    nodeConfigurations: NodeConfigurationsMap
