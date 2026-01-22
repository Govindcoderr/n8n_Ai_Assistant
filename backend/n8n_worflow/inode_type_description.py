from dataclasses import dataclass, field
from typing import List, TypedDict, Union, Optional, Dict


@dataclass
class INodeTypeDescription:
    name: str
    displayName: str
    description: str = ""
    version: Union[int, List[int]] = 1

    inputs: Union[str, List[str]] = field(default_factory=list)
    outputs: Union[str, List[str]] = field(default_factory=list)

    codex: Optional[Dict] = None

# today add for node add tool and other utils 
class INode(TypedDict, total=False):
    id: str
    name: str
    type: str
    typeVersion: int
    position: List[int]           # [x, y]
    parameters: Dict[str, any]
    credentials: Optional[Dict[str, any]]
    webhookId: Optional[str]
    disabled: Optional[bool]


class IConnections(TypedDict, total=False):
    # Example structure: { "main": { "0": [{"node": "NodeName", "type": "main", "index": 0}] } }
    main: Optional[Dict[str, List[List[Dict[str, Union[str, int]]]]]]
    # You can add other connection types if needed (e.g. "ai", "trigger", etc.)

class IWorkflowBase(TypedDict, total=False):
    id: Optional[str]
    name: str
    nodes: List[INode]
    connections: IConnections
    active: Optional[bool]
    settings: Optional[Dict[str, any]]
    # ... other fields you might need

class INodeParameters(TypedDict, total=False):
    # Define parameters as needed; using a generic dictionary for flexibility
    pass