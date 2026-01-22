from typing import Optional, Union, List, Any

from backend.n8n_worflow.inode_type_description import INode, INodeTypeDescription  

# Constants (matching n8n-workflow)
NodeConnectionTypes = {
    "Main": "main",
    "Trigger": "trigger",
    "actions": "actions",
}


def is_sub_node(
    node_type: INodeTypeDescription,
    node: Optional[INode] = None
) -> bool:
    """
    Determines whether a node should be treated as a "sub-node" in the workflow canvas.
    
    Sub-nodes are nodes that:
    - Have no main input connections
    - Only have AI inputs (or no inputs at all)
    - Special cases like Vector Store in "retrieve-as-tool" mode
    
    Returns:
        True if the node is considered a sub-node, False otherwise
    """
    # Special case: Vector Store in "retrieve-as-tool" mode is always a sub-node
    if node and node.get("parameters", {}).get("mode") == "retrieve-as-tool":
        return True

    # Agents are always treated as main nodes
    if node_type["name"] == "@n8n/n8n-nodes-langchain.agent":
        return False

    # No inputs defined → definitely sub-node
    inputs = node_type.get("inputs")
    if inputs is None or (isinstance(inputs, list) and len(inputs) == 0):
        return True

    # Case 1: inputs is a list (static inputs)
    if isinstance(inputs, list):
        has_main_input = False
        for input_def in inputs:
            if isinstance(input_def, str):
                if input_def.lower() == "main":
                    has_main_input = True
                    break
            elif isinstance(input_def, dict):
                # INodeInputConfiguration shape
                if input_def.get("type", "").lower() == "main":
                    has_main_input = True
                    break

        return not has_main_input

    # Case 2: inputs is a string (expression/dynamic inputs)
    if isinstance(inputs, str):
        inputs_lower = inputs.lower()

        main_input_indicators = [
            'nodeconnectiontypes.main',
            'type: "main"',
            "type: 'main'",
            'type:"main"',
            "type:'main'",
            'type: `main`',
            'type: nodeconnectiontypes.main',
            'type:nodeconnectiontypes.main',
            '{ displayname: "", type: "main"',
            "{ displayname: '', type: 'main'",
            '{ displayname: "", type: nodeconnectiontypes.main',
            "{ displayname: '', type: nodeconnectiontypes.main",
            'return ["main"',
            "return ['main'",
            'return [`main`',
            'return[["main"',
            "return[['main'",
            'return [[`main`',
            '["main", ...',
            "['main', ...",
            '[`main`, ...',
        ]

        # If **any** of these patterns appear → likely has main input
        has_main_input = any(pattern.lower() in inputs_lower for pattern in main_input_indicators)
        return not has_main_input

    # Fallback: unknown/unsupported inputs shape → treat as main node (safer)
    return False

# Optional: convenience aliases / exports
isSubNode = is_sub_node  