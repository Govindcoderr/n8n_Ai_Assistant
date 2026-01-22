"""
Node creation and utility functions for n8n-like workflow system.
"""

import uuid
from typing import List, Tuple, Dict, Any, Union, Optional

from backend.n8n_worflow.inode_type_description import INode, INodeTypeDescription 




def generate_unique_name(base_name: str, existing_nodes: List[INode]) -> str:
    """
    Generate a unique node name by appending incrementing numbers if necessary.

    Args:
        base_name: Desired base name for the node
        existing_nodes: List of current nodes in the workflow

    Returns:
        A unique node name
    """
    if not base_name:
        base_name = "Node"

    unique_name = base_name
    counter = 1

    existing_names = {node["name"] for node in existing_nodes if "name" in node}

    while unique_name in existing_names:
        unique_name = f"{base_name}{counter}"
        counter += 1

    return unique_name


def get_latest_version(node_type: INodeTypeDescription) -> int:
    """
    Determine the latest (or default) version number for a given node type.

    Args:
        node_type: Node type definition

    Returns:
        Latest version number

    Raises:
        ValueError: If version information is invalid/missing
    """
    # Prefer defaultVersion if explicitly set
    if hasattr(node_type, "defaultVersion") and node_type.defaultVersion is not None:
        return node_type.defaultVersion

    version = node_type.version

    if version is None:
        raise ValueError(f"Node type {node_type.name} has no version information")


    if isinstance(version, int):
        return version

    if isinstance(version, list) and version:
        return max(version)  # usually last = latest

    raise ValueError(
        f"Invalid version format for node type {node_type.get('name', 'unknown')}: {version}"
    )


def generate_node_id() -> str:
    """Generate a random UUID for node identification"""
    return str(uuid.uuid4())


def generate_webhook_id() -> str:
    """Generate a random UUID for webhook identification"""
    return str(uuid.uuid4())


def requires_webhook(node_type: INodeTypeDescription) -> bool:
    """
    Check if the node type requires a webhook ID (typically trigger/webhook nodes)
    """
    # webhooks = node_type.get("webhooks")
    webhooks = getattr(node_type, "webhooks", None)
    return bool(webhooks and len(webhooks) > 0)


def create_node_instance(
    node_type: INodeTypeDescription,
    type_version: int,
    name: str,
    position: Tuple[int, int],
    parameters: Optional[Dict[str, Any]] = None,
    node_id: Optional[str] = None,
) -> INode:
    """
    Create a complete node instance ready to be added to a workflow.

    Args:
        node_type: Full node type definition
        type_version: Chosen version of the node
        name: Unique name for this node instance
        position: Canvas position [x, y]
        parameters: Node parameters (will NOT be merged with defaults here)
        node_id: Optional explicit ID (mainly for testing/reproducibility)

    Returns:
        Fully formed node dictionary

    Raises:
        ValueError: If requested version is not supported by the node type
    """
    # Validate version compatibility
    version = node_type.version
    if isinstance(version, list):
        if type_version not in version:
            raise ValueError(
                f"Version {type_version} is not valid for node {node_type.name}. "
                f"Supported versions: {version}"
            )
    elif isinstance(version, int):
        if type_version != version:
            raise ValueError(
                f"Node {node_type.name} only supports version {version}, "
                f"requested: {type_version}"
            )
    elif version is not None:
        raise ValueError(f"Unexpected version format: {version}")

    node: INode = {
    "id": node_id if node_id else generate_node_id(),
    "name": name,
    "type": node_type.name,
    "typeVersion": type_version,
    "position": list(position),
    "parameters": parameters or {},
}


    if requires_webhook(node_type):
        node["webhookId"] = generate_webhook_id()

    return node


def merge_with_defaults(
    parameters: Dict[str, Any],
    node_type: INodeTypeDescription,
) -> Dict[str, Any]:
    """
    Merge user-provided parameters with the node type's default values.
    User values take precedence.
    """
    defaults = getattr(node_type, "defaults", {}) or {}
    return {**defaults, **(parameters or {})}


# ─── Convenience combined function ─────────────────────────────────────

def create_node(
    node_type: INodeTypeDescription,
    name: str,
    position: Tuple[int, int],
    parameters: Optional[Dict[str, Any]] = None,
    type_version: Optional[int] = None,
    node_id: Optional[str] = None,
) -> INode:
    """
    High-level helper: create node with latest version and merged parameters.

    This is the most commonly used function in real applications.
    """
    version = type_version if type_version is not None else get_latest_version(node_type)

    # Merge defaults first, then apply user overrides
    merged_params = merge_with_defaults(parameters or {}, node_type)

    return create_node_instance(
        node_type=node_type,
        type_version=version,
        name=name,
        position=position,
        parameters=merged_params,
        node_id=node_id,
    )