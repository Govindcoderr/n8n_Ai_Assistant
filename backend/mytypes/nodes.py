from typing import List, Dict, Any, Optional, Union, TypedDict

# Reference for INodeParameters from n8n-workflow
INodeParameters = Dict[str, Any]

# Reference for AddedNode, NodeDetails, NodeSearchResult
class NodeDetails(TypedDict, total=False):
    name: str
    displayName: str
    description: str
    properties: List[Dict[str, Any]]  # INodeProperties equivalent
    subtitle: Optional[str]
    inputs: Any
    outputs: Any

class NodeSearchResult(TypedDict, total=False):
    name: str
    displayName: str
    description: str
    version: int
    score: float
    inputs: Any
    outputs: Any

class AddedNode(TypedDict, total=False):
    id: str
    name: str
    type: str
    displayName: Optional[str]
    parameters: Optional[INodeParameters]
    position: List[int]  # [x, y] coordinates

# Types of progress updates
# ProgressUpdateType = Union['input', 'output', 'progress', 'error']

# Progress update during tool execution
# class ProgressUpdate(TypedDict, total=False):
#     type: ProgressUpdateType
#     data: Dict[str, Any]
#     timestamp: Optional[str]

# Tool progress message
# class ToolProgressMessage(TypedDict, total=False):
#     type: str  # always 'tool'
#     toolName: str
#     toolCallId: Optional[str]
#     status: str  # 'running', 'completed', 'error'
#     updates: List[ProgressUpdate]
#     displayTitle: Optional[str]
#     customDisplayTitle: Optional[str]

# Tool execution error
class ToolError(TypedDict, total=False):
    message: str
    code: Optional[str]
    details: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]]

# Progress reporter interface
class ProgressReporter(TypedDict, total=False):
    start: Any  # callable
    progress: Any  # callable
    complete: Any  # callable
    error: Any  # callable
    createBatchReporter: Any  # callable

# Batch progress reporter for multi-item operations
class BatchReporter(TypedDict, total=False):
    init: Any  # callable
    next: Any  # callable
    complete: Any  # callable

# Output types for various tools
class UpdateNodeParametersOutput(TypedDict, total=False):
    nodeId: str
    nodeName: str
    nodeType: str
    updatedParameters: INodeParameters
    appliedChanges: List[str]
    message: str

class AddNodeOutput(TypedDict, total=False):
    addedNode: AddedNode
    message: str

class ConnectNodesOutput(TypedDict, total=False):
    sourceNode: str
    targetNode: str
    connectionType: str
    swapped: bool
    message: str
    found: Dict[str, bool]

class RemoveNodeOutput(TypedDict, total=False):
    removedNodeId: str
    removedNodeName: str
    removedNodeType: str
    connectionsRemoved: int
    message: str

class NodeDetailsOutput(TypedDict, total=False):
    details: NodeDetails
    found: bool
    message: str

class NodeSearchOutput(TypedDict, total=False):
    results: List[Dict[str, Any]]  # query + results
    totalResults: int   
    message: str

class GetNodeParameterOutput(TypedDict, total=False):
    message: str  # success or error only

class RemoveConnectionOutput(TypedDict, total=False):
    sourceNode: str
    targetNode: str
    connectionType: str
    sourceOutputIndex: int
    targetInputIndex: int
    message: str

class CategorizePromptOutput(TypedDict, total=False):
    categorization: Dict[str, Any]  # PromptCategorization placeholder

class SimpleWorkflow(TypedDict, total=False):
    nodes: List[Dict[str, Any]]
    connections: Dict[str, Any]

class WorkflowMetadata(TypedDict, total=False):
    name: str
    description: Optional[str]
    workflow: SimpleWorkflow

class NodeConfigurationEntry(TypedDict, total=False):
    version: int
    parameters: INodeParameters

NodeConfigurationsMap = Dict[str, List[NodeConfigurationEntry]]

class GetWorkflowExamplesOutput(TypedDict, total=False):
    examples: List[Dict[str, Any]]  # name, description?, workflow
    totalResults: int
    nodeConfigurations: NodeConfigurationsMap
