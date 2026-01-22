import uuid
from typing import List, Tuple, Dict, Any, Union

from backend.n8n_worflow.inode_type_description import (   
    INode,
    INodeTypeDescription,
    NodeParameterValueType,
)


def generate_unique_name(base_name: str, existing_nodes: List[INode]) -> str:
    """
    Generate a unique node name by appending numbers if necessary
    
    Args:
        base_name: The base name to start with
        existing_nodes: List of existing nodes to check against
        
    Returns:
        A unique node name
    """
    unique_name = base_name
    counter = 1

    existing_names = {node["name"] for node in existing_nodes}

    while unique_name in existing_names:
        unique_name = f"{base_name}{counter}"
        counter += 1

    return unique_name


def get_latest_version(node_type: INodeTypeDescription) -> int:
    """
    Get the latest version number for a node type
    
    Args:
        node_type: The node type description
        
    Returns:
        The latest version number
    """
    if hasattr(node_type, "defaultVersion") and node_type["defaultVersion"] is not None:
        return node_type["defaultVersion"]

    version = node_type["version"]

    if isinstance(version, int):
        return version

    if isinstance(version, list):
        return version[-1]

    raise ValueError(
        f"Unexpected version format for node type {node_type['name']}: {version}"
    )


def generate_node_id() -> str:
    """Generate a unique node ID"""
    return str(uuid.uuid4())


def generate_webhook_id() -> str:
    """Generate a unique webhook ID for nodes that require it"""
    return str(uuid.uuid4())


def requires_webhook(node_type: INodeTypeDescription) -> bool:
    """
    Check if a node type requires a webhook
    
    Returns:
        True if the node requires a webhook
    """
    webhooks = node_type.get("webhooks")
    return bool(webhooks and len(webhooks) > 0)


def create_node_instance(
    node_type: INodeTypeDescription,
    type_version: int,
    name: str,
    position: Tuple[int, int],
    parameters: Dict[str, NodeParameterValueType] = None,
    node_id: str = None,
) -> INode:
    """
    Create a new node instance with all required properties
    
    Args:
        node_type: The node type description
        type_version: The node type version
        name: The name for the node
        position: The canvas position of the node [x, y]
        parameters: Optional parameters for the node
        node_id: Optional specific ID (mainly for testing)
        
    Returns:
        Complete node dictionary
    """
    # Validate version compatibility
    version = node_type["version"]
    if isinstance(version, list):
        if type_version not in version:
            raise ValueError(
                f"Version {type_version} is not valid for node type {node_type['name']}. "
                f"Allowed versions: {version}"
            )
    elif isinstance(version, int):
        if type_version != version:
            raise ValueError(
                f"Node type {node_type['name']} only supports version {version}, "
                f"requested: {type_version}"
            )
    else:
        raise ValueError(f"Unexpected version format: {version}")

    node: INode = {
        "id": node_id or generate_node_id(),
        "name": name,
        "type": node_type["name"],
        "typeVersion": type_version,
        "position": list(position),  # usually we store as array in n8n
        "parameters": parameters or {},
    }

    # Add webhook ID if this node type requires it
    if requires_webhook(node_type):
        node["webhookId"] = generate_webhook_id()

    return node


def merge_with_defaults(
    parameters: Dict[str, NodeParameterValueType],
    node_type: INodeTypeDescription,
) -> Dict[str, NodeParameterValueType]:
    """
    Merge provided parameters with node defaults
    
    Args:
        parameters: User-provided parameters
        node_type: The node type description
        
    Returns:
        Merged parameters dictionary
    """
    defaults = node_type.get("defaults", {})
    return {**defaults, **(parameters or {})}


# Optional: Small helper for more readable code when you often want the latest version
def create_node_latest(
    node_type: INodeTypeDescription,
    name: str,
    position: Tuple[int, int],
    parameters: Dict[str, NodeParameterValueType] = None,
    node_id: str = None,
) -> INode:
    """Convenience function - creates node using latest available version"""
    version = get_latest_version(node_type)
    return create_node_instance(
        node_type=node_type,
        type_version=version,
        name=name,
        position=position,
        parameters=parameters,
        node_id=node_id,
    )