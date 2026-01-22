# """
# Workflow state helpers and update creators.
# These functions help read current workflow state and create immutable update operations.
# """

# from typing import Dict, Any, List, Union, Optional

# from backend.mytypes.nodes import SimpleWorkflow
# from backend.n8n_worflow.inode_type_description import INode, IConnections


# # For type safety and IDE support
# WorkflowStateType = Dict[str, Any]  # typeof WorkflowState.State


# def get_current_workflow(state: WorkflowStateType) -> SimpleWorkflow:
#     """
#     Safely extract current workflow from state.
    
#     Returns:
#         SimpleWorkflow containing name, nodes, connections
#     """
#     return state.get("workflowJSON", {
#         "name": "Untitled Workflow",
#         "nodes": [],
#         "connections": {}
#     })


# def get_workflow_state() -> WorkflowStateType:  
#     return {
#         "workflowJSON": {
#             "name": "Example Workflow",
#             "nodes": [],
#             "connections": {}
#         }
#      }  

    



# def get_current_workflow_from_task_input() -> SimpleWorkflow:
#     """Convenience function: get workflow directly from current task input"""
#     state = get_workflow_state()
#     return get_current_workflow(state)

# # ─── State Update Creators ──────────────────────────────────────────────────

# def update_workflow_connections(
#     connections: Dict[str, Any]  # SimpleWorkflow['connections']
# ) -> Dict[str, Any]:
#     """
#     Create a state update that merges new connections (does NOT replace existing ones)
#     """
#     return {
#         "workflowOperations": [
#             {
#                 "type": "mergeConnections",
#                 "connections": connections
#             }
#         ]
#     }

# def add_node_to_workflow(node: INode) -> Dict[str, Any]:
#     """Create state update to add a single node"""
#     return add_nodes_to_workflow([node])


# def add_nodes_to_workflow(nodes: List[INode]) -> Dict[str, Any]:
#     """Create state update to add multiple nodes"""
#     return {
#         "workflowOperations": [
#             {
#                 "type": "addNodes",
#                 "nodes": nodes
#             }
#         ]
#     }


# def remove_node_from_workflow(node_id: str) -> Dict[str, Any]:
#     """Create state update to remove a single node by ID"""
#     return remove_nodes_from_workflow([node_id])


# def remove_nodes_from_workflow(node_ids: List[str]) -> Dict[str, Any]:
#     """Create state update to remove multiple nodes"""
#     return {
#         "workflowOperations": [
#             {
#                 "type": "removeNode",
#                 "nodeIds": node_ids
#             }
#         ]
#     }


# def update_node_in_workflow(
#     state: WorkflowStateType,
#     node_id: str,
#     updates: Dict[str, Any]  # Partial<INode>
# ) -> Dict[str, Any]:
#     """
#     Create state update to modify an existing node.
#     Returns empty dict if node doesn't exist.
#     """
#     workflow = get_current_workflow(state)
#     existing_node = next((n for n in workflow["nodes"] if n["id"] == node_id), None)
    
#     if not existing_node:
#         return {}
        
#     return {
#         "workflowOperations": [
#             {
#                 "type": "updateNode",
#                 "nodeId": node_id,
#                 "updates": updates
#             }
#         ]
#     }


# def add_connection_to_workflow(
#     source_node_id: str,
#     target_node_id: str,
#     connection: IConnections
# ) -> Dict[str, Any]:
#     """
#     Create state update to add a single connection.
#     Uses mergeConnections operation.
#     """
#     connections_patch = {
#         source_node_id: {
#             "main": [[connection]]  # n8n connection format: array of arrays
#         }
#     }
    
#     return {
#         "workflowOperations": [
#             {
#                 "type": "mergeConnections",
#                 "connections": connections_patch
#             }
#         ]
#     }


# def remove_connection_from_workflow(
#     source_node: str,
#     target_node: str,
#     connection_type: str = "main",
#     source_output_index: int = 0,
#     target_input_index: int = 0
# ) -> Dict[str, Any]:
#     """
#     Create state update to remove a specific connection.
#     """
#     return {
#         "workflowOperations": [
#             {
#                 "type": "removeConnection",
#                 "sourceNode": source_node,
#                 "targetNode": target_node,
#                 "connectionType": connection_type,
#                 "sourceOutputIndex": source_output_index,
#                 "targetInputIndex": target_input_index,
#             }
#         ]
#     }


"""
Workflow state helpers and update creators.
These functions help read current workflow state and create immutable update operations.
"""

from typing import Dict, Any, List

from backend.mytypes.nodes import SimpleWorkflow
from backend.n8n_worflow.inode_type_description import INode, IConnections


# Workflow state is always a DICT
WorkflowStateType = Dict[str, Any]


# ─────────────────────────────────────────────────────────────
# Core workflow getters
# ─────────────────────────────────────────────────────────────

def get_workflow_state() -> WorkflowStateType:
    """
    Return the current workflow state.
    In real systems this will come from task/session/context.
    """
    return {
        "workflowJSON": {
            "name": "Example Workflow",
            "nodes": [],
            "connections": {},
        }
    }


def get_current_workflow(state: WorkflowStateType) -> SimpleWorkflow:
    """
    Safely extract workflow JSON from state.
    ALWAYS returns a dict with nodes + connections.
    """
    return state.get(
        "workflowJSON",
        {
            "name": "Untitled Workflow",
            "nodes": [],
            "connections": {},
        },
    )


# ─────────────────────────────────────────────────────────────
# Workflow update creators
# ─────────────────────────────────────────────────────────────

def add_node_to_workflow(node: INode) -> Dict[str, Any]:
    """Create state update to add a single node"""
    return add_nodes_to_workflow([node])


def add_nodes_to_workflow(nodes: List[INode]) -> Dict[str, Any]:
    """Create state update to add multiple nodes"""
    return {
        "workflowOperations": [
            {
                "type": "addNodes",
                "nodes": nodes,
            }
        ]
    }


def remove_node_from_workflow(node_id: str) -> Dict[str, Any]:
    """Create state update to remove a single node"""
    return remove_nodes_from_workflow([node_id])


def remove_nodes_from_workflow(node_ids: List[str]) -> Dict[str, Any]:
    """Create state update to remove multiple nodes"""
    return {
        "workflowOperations": [
            {
                "type": "removeNode",
                "nodeIds": node_ids,
            }
        ]
    }


def update_node_in_workflow(
    state: WorkflowStateType,
    node_id: str,
    updates: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Create state update to modify an existing node.
    Returns empty dict if node doesn't exist.
    """
    workflow = get_current_workflow(state)

    existing_node = next(
        (n for n in workflow["nodes"] if n.get("id") == node_id),
        None,
    )

    if not existing_node:
        return {}

    return {
        "workflowOperations": [
            {
                "type": "updateNode",
                "nodeId": node_id,
                "updates": updates,
            }
        ]
    }


def update_workflow_connections(
    connections: Dict[str, Any],
) -> Dict[str, Any]:
    """Merge new connections into workflow"""
    return {
        "workflowOperations": [
            {
                "type": "mergeConnections",
                "connections": connections,
            }
        ]
    }


def add_connection_to_workflow(
    source_node_id: str,
    target_node_id: str,
    connection: IConnections,
) -> Dict[str, Any]:
    """Create state update to add a single connection"""
    return {
        "workflowOperations": [
            {
                "type": "mergeConnections",
                "connections": {
                    source_node_id: {
                        "main": [[connection]],
                    }
                },
            }
        ]
    }


def remove_connection_from_workflow(
    source_node: str,
    target_node: str,
    connection_type: str = "main",
    source_output_index: int = 0,
    target_input_index: int = 0,
) -> Dict[str, Any]:
    """Create state update to remove a specific connection"""
    return {
        "workflowOperations": [
            {
                "type": "removeConnection",
                "sourceNode": source_node,
                "targetNode": target_node,
                "connectionType": connection_type,
                "sourceOutputIndex": source_output_index,
                "targetInputIndex": target_input_index,
            }
        ]
    }
