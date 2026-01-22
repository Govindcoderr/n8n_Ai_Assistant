from typing import List, Optional, Dict, Any, Union

# Assuming these are your custom exception classes
from backend.error import (
    ConnectionError,
    NodeNotFoundError,
    NodeTypeNotFoundError,
    ParameterTooLargeError,
    ValidationError,
)

from backend.n8n_worflow.inode_type_description import INode, INodeTypeDescription  # ← your type definitions

from backend.mytypes.tools import ToolError
from backend.mytypes.workflow import SimpleWorkflow


def validate_node_exists(node_id: str, nodes: List[INode]) -> Optional[INode]:
    """
    Validate that a node exists in the workflow by ID
    
    Returns:
        The found node or None if not found
    """
    for node in nodes:
        if node["id"] == node_id:
            return node
    return None


def find_node_by_name(node_name: str, nodes: List[INode]) -> Optional[INode]:
    """
    Find a node by name (case-insensitive)
    
    Returns:
        The found node or None
    """
    search_name = node_name.lower()
    for node in nodes:
        if node["name"].lower() == search_name:
            return node
    return None


def find_node_by_id_or_name(node_identifier: str, nodes: List[INode]) -> Optional[INode]:
    """
    Find a node by either ID (preferred) or name
    
    Returns:
        The found node or None
    """
    # First try exact ID match
    by_id = validate_node_exists(node_identifier, nodes)
    if by_id is not None:
        return by_id

    # Then try name match (case-insensitive)
    return find_node_by_name(node_identifier, nodes)


def find_node_type(
    node_type_name: str,
    node_version: int,
    node_types: List[INodeTypeDescription]
) -> Optional[INodeTypeDescription]:
    """
    Find a node type by name and exact version
    
    Returns:
        Matching node type description or None
    """
    for nt in node_types:
        if nt.name != node_type_name:
            continue

        version = nt.version
        if isinstance(version, list):
            if node_version in version:
                return nt
        elif isinstance(version, int):
            if version == node_version:
                return nt

    return None


def validate_connection(source_node: INode, target_node: INode) -> Optional[ToolError]:
    """
    Validate that a connection is possible between two nodes
    
    Returns:
        ToolError if invalid, None if valid
    """
    if source_node["id"] == target_node["id"]:
        error = ConnectionError(
            "Cannot connect a node to itself",
            extra={
                "fromNodeId": source_node["id"],
                "toNodeId": target_node["id"],
            }
        )
        return {
            "message": str(error),
            "code": "SELF_CONNECTION",
            "details": {
                "sourceId": source_node["id"],
                "targetId": target_node["id"]
            }
        }

    return None


def create_validation_error(
    message: str,
    code: str,
    details: Optional[Dict[str, str]] = None
) -> ToolError:
    """Create a standardized validation error response"""
    error = ValidationError(message, tags={"code": code, **(details or {})})
    return {
        "message": str(error),
        "code": code,
        "details": details or {}
    }


def create_node_not_found_error(node_identifier: str) -> ToolError:
    """Create standardized 'node not found' error"""
    error = NodeNotFoundError(node_identifier)
    return {
        "message": str(error),
        "code": "NODE_NOT_FOUND",
        "details": {"nodeIdentifier": node_identifier}
    }


def create_node_type_not_found_error(node_type_name: str) -> ToolError:
    """Create standardized 'node type not found' error"""
    error = NodeTypeNotFoundError(node_type_name)
    return {
        "message": str(error),
        "code": "NODE_TYPE_NOT_FOUND",
        "details": {"nodeTypeName": node_type_name}
    }


def create_node_parameter_too_large_error(
    node_id: str,
    parameter: str,
    max_size: int
) -> ToolError:
    """Create standardized 'parameter value too large' error"""
    error = ParameterTooLargeError(
        "Parameter value is too large to retrieve",
        extra={
            "parameter": parameter,
            "nodeId": node_id,
            "maxSize": max_size
        }
    )

    return {
        "message": str(error),
        "code": "NODE_PARAMETER_TOO_LARGE",
        "details": {
            "nodeId": node_id,
            "parameter": parameter,
            "maxSize": str(max_size)
        }
    }


def has_nodes(workflow: SimpleWorkflow) -> bool:
    """Check if a workflow contains any nodes"""
    return len(workflow["nodes"]) > 0