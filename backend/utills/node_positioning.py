"""
Node positioning utilities for n8n-like workflow canvas.
These functions help calculate smart positions for new nodes to keep the workflow visually organized.
"""

from typing import List, Tuple, Dict, Any, Optional
from backend.n8n_worflow.inode_type_description import INode, INodeTypeDescription
from backend.utills.node_helpers import is_sub_node


# ─── Positioning Configuration ───────────────────────────────────────────────

POSITIONING_CONFIG = {
    "HORIZONTAL_GAP": 280,               # Gap between columns of nodes
    "MAIN_NODE_Y": 300,                  # Base Y for main flow nodes
    "SUB_NODE_Y": 450,                   # Base Y for sub-nodes (below main)
    "VERTICAL_SPACING": 120,             # Vertical spacing between nodes in same column
    "INITIAL_X": 250,                    # Starting X position for first node
    "X_PROXIMITY_THRESHOLD": 50,         # Tolerance to consider nodes at same X
    "SUB_NODE_HORIZONTAL_OFFSET": 0.8,   # Multiplier for spreading sub-nodes horizontally
}


def calculate_node_position(
    existing_nodes: List[INode],
    is_sub_node_type: bool,
    node_types: List[INodeTypeDescription],
) -> Tuple[int, int]:
    """
    Calculate the best [x, y] position for a new node.
    
    Args:
        existing_nodes: Current nodes in the workflow
        is_sub_node_type: Whether the new node is a sub-node
        node_types: All available node type definitions
        
    Returns:
        Tuple (x, y) position
    """
    cfg = POSITIONING_CONFIG

    if not existing_nodes:
        # First node
        y = cfg["SUB_NODE_Y"] if is_sub_node_type else cfg["MAIN_NODE_Y"]
        return (cfg["INITIAL_X"], y)

    main_nodes, sub_nodes = categorize_nodes(existing_nodes, node_types)

    # Calculate X
    target_x = _calculate_x_position(is_sub_node_type, main_nodes, sub_nodes)

    # Calculate Y (avoid vertical collisions)
    target_y = _calculate_y_position(target_x, existing_nodes, is_sub_node_type)

    return (target_x, target_y)


def categorize_nodes(
    nodes: List[INode],
    node_types: List[INodeTypeDescription],
) -> Dict[str, List[INode]]:
    """
    Split nodes into main nodes and sub-nodes.
    """
    main_nodes: List[INode] = []
    sub_nodes: List[INode] = []

    for node in nodes:
        node_type = next((nt for nt in node_types if nt.name == node.type), None)
        if node_type and is_sub_node(node_type, node):
            sub_nodes.append(node)
        else:
            main_nodes.append(node)

    return {"main_nodes": main_nodes, "sub_nodes": sub_nodes}


def _calculate_x_position(
    is_sub_node_type: bool,
    main_nodes: List[INode],
    sub_nodes: List[INode],
) -> int:
    """Internal helper - calculate horizontal position"""
    cfg = POSITIONING_CONFIG

    if is_sub_node_type:
        # Sub-nodes: spread horizontally under main nodes
        if main_nodes:
            min_main_x = min(n["position"][0] for n in main_nodes)
            return int(min_main_x + len(sub_nodes) * (cfg["HORIZONTAL_GAP"] * cfg["SUB_NODE_HORIZONTAL_OFFSET"]))
        return cfg["INITIAL_X"]
    else:
        # Main nodes: always go to the right
        if main_nodes:
            max_main_x = max(n.position[0] for n in main_nodes)
            return max_main_x + cfg["HORIZONTAL_GAP"]
        return cfg["INITIAL_X"]


def _calculate_y_position(
    target_x: int,
    existing_nodes: List[INode],
    is_sub_node_type: bool,
) -> int:
    """Internal helper - calculate vertical position with collision avoidance"""
    cfg = POSITIONING_CONFIG

    base_y = cfg["SUB_NODE_Y"] if is_sub_node_type else cfg["MAIN_NODE_Y"]

    # Find nodes close to target X
    nodes_at_x = [
        n for n in existing_nodes
        if abs(n.position[0] - target_x) < cfg["X_PROXIMITY_THRESHOLD"]
    ]

    # Stack vertically below existing nodes at this column
    vertical_offset = len(nodes_at_x) * cfg["VERTICAL_SPACING"]
    return base_y + vertical_offset


def get_nodes_at_position(
    nodes: List[INode],
    position: Tuple[int, int],
    tolerance: int = 50,
) -> List[INode]:
    """
    Find all nodes near a given position (with tolerance).
    Useful for collision detection or snap-to-grid logic.
    """
    x, y = position
    return [
        node for node in nodes
        if abs(node.position[0] - x) < tolerance
        and abs(node.position[1] - y) < tolerance

    ]


def calculate_connected_node_position(
    source_node: INode,
    is_target_sub_node: bool,
    existing_nodes: List[INode],
    node_types: List[INodeTypeDescription],  # kept for consistency (can be removed if unused)
) -> Tuple[int, int]:
    """
    Calculate position for a node that should be connected to a source node.
    
    - Sub-nodes → below source
    - Main nodes → to the right of source
    """
    cfg = POSITIONING_CONFIG

    if is_target_sub_node:
        # Sub-node: place below source
        target_x = source_node.position[0]
        target_y = cfg["SUB_NODE_Y"]

        # Avoid collision with other nearby sub-nodes
        nearby_sub_nodes = [
            n for n in existing_nodes
            if abs(n.position[0] - target_x) < 50
            and cfg["SUB_NODE_Y"] <= n.position[1] < cfg["SUB_NODE_Y"] + cfg["VERTICAL_SPACING"] * 5
        ]

        return (target_x, target_y + len(nearby_sub_nodes) * cfg["VERTICAL_SPACING"])

    else:
        # Main node: place to the right
        target_x = source_node.position[0] + cfg["HORIZONTAL_GAP"]
        target_y = source_node.position[1]

        nodes_at_pos = get_nodes_at_position(existing_nodes, (target_x, target_y))
        return (target_x, target_y + len(nodes_at_pos) * cfg["VERTICAL_SPACING"])