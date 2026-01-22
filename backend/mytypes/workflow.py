"""
Workflow-related type definitions for the n8n-like builder application.
"""

from typing import Dict, List, Literal, Union, TypedDict, Optional

from backend.n8n_worflow.inode_type_description import INode , IConnections 



# ─── Simplified workflow for most builder operations ─────────────────────────

class SimpleWorkflow(TypedDict):
    name: str
    nodes: List[INode]
    connections: IConnections


# ─── Workflow operation types (immutable actions for state management) ───────

class ClearOperation(TypedDict):
    type: Literal["clear"]


class RemoveNodeOperation(TypedDict):
    type: Literal["removeNode"]
    nodeIds: List[str]


class AddNodesOperation(TypedDict):
    type: Literal["addNodes"]
    nodes: List[INode]


class UpdateNodeOperation(TypedDict):
    type: Literal["updateNode"]
    nodeId: str
    updates: Dict[str, any]  # Partial<INode> - any subset of INode fields


class SetConnectionsOperation(TypedDict):
    type: Literal["setConnections"]
    connections: IConnections


class MergeConnectionsOperation(TypedDict):
    type: Literal["mergeConnections"]
    connections: IConnections


class RemoveConnectionOperation(TypedDict):
    type: Literal["removeConnection"]
    sourceNode: str
    targetNode: str
    connectionType: str           # usually "main", can be others
    sourceOutputIndex: int
    targetInputIndex: int


class SetNameOperation(TypedDict):
    type: Literal["setName"]
    name: str


# Union of all possible workflow operations
WorkflowOperation = Union[
    ClearOperation,
    RemoveNodeOperation,
    AddNodesOperation,
    UpdateNodeOperation,
    SetConnectionsOperation,
    MergeConnectionsOperation,
    RemoveConnectionOperation,
    SetNameOperation,
]