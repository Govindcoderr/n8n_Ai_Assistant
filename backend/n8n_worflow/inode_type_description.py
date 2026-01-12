from dataclasses import dataclass, field
from typing import List, Union, Optional, Dict


@dataclass
class INodeTypeDescription:
    name: str
    displayName: str
    description: str = ""
    version: Union[int, List[int]] = 1

    inputs: Union[str, List[str]] = field(default_factory=list)
    outputs: Union[str, List[str]] = field(default_factory=list)

    codex: Optional[Dict] = None
