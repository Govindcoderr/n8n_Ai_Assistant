# import os
# from typing import Dict, Any, Optional, List

# from langchain.tools import tool 

# from pydantic import BaseModel, Field, ValidationError as PydanticValidationError

# # n8n workflow core types
# from backend.n8n_worflow.inode_type_description   import (
#     INode,
#     INodeTypeDescription,
#     INodeParameters,
# )

# from backend.utills.stream_processor import BuilderToolBase , BuilderTool

# # Errors
# from backend.error import NodeTypeNotFoundError, ValidationError
# # Node utilities
# from backend.utills.node_creation import (
#     create_node_instance,
#     generate_unique_name,
# )
# from backend.utills.node_positioning import calculate_node_position
# from backend.utills.node_helpers import is_sub_node

# # Helpers
# from backend.mytools.helpers.progress  import createProgressReporter
# from backend.mytools.helpers.response import create_success_response, create_error_response
# from backend.mytools.helpers.state import (
#     get_current_workflow,
#     add_node_to_workflow,
#     get_workflow_state,
# )
# from backend.mytools.helpers.validation import find_node_type

# # Types
# from backend.mytypes.nodes import AddedNode
# from backend.mytypes.tools import AddNodeOutput, ToolError

# # Input Schemas

# class NodeCreationSchema(BaseModel):
#        nodeType: str = Field(description="The type of node to add")
#        nodeVersion: int = Field(description="Exact node version")
#        name: str = Field(description="Descriptive node name")
#        connectionParametersReasoning: str = Field(description="REQUIRED: Explain why connection parameters are chosen")
#        connectionParameters: Dict[str, Any] = Field(
#        default_factory=dict,
#        description="Only connection-affecting parameters"
#       )

# class NodeCreationE2ESchema(NodeCreationSchema):
#     id: Optional[str] = Field(
#         None,
#         description="Optional deterministic node ID (E2E tests only)",
#     )


# # ---------------------------------------------------------------------
# # Core Node Creation Logic
# # ---------------------------------------------------------------------

# def create_node(
#     node_type: INodeTypeDescription,
#     type_version: int,
#     custom_name: str,
#     existing_nodes: List[INode],
#     node_types: List[INodeTypeDescription],
#     connection_parameters: Optional[INodeParameters] = None,
#     node_id: Optional[str] = None,
# ) -> INode:
#     base_name = (
#         custom_name
#         or getattr(node_type.defaults, "name", None)
#         or node_type.displayName
#     )

#     unique_name = generate_unique_name(base_name, existing_nodes)

#     position = calculate_node_position(
#         existing_nodes,
#         is_sub_node(node_type),
#         node_types,
#     )

#     return create_node_instance(
#         node_type=node_type,
#         type_version=type_version,
#         name=unique_name,
#         position=position,
#         parameters=connection_parameters,
#         node_id=node_id,
#     )


# def build_response_message(
#     added_node: AddedNode,
#     node_types: List[INodeTypeDescription],
# ) -> str:
#     node_type = next(
#         (nt for nt in node_types if nt.name == added_node.type),
#         None,
#     )

#     sub_node_info = (
#         " (sub-node)" if node_type and is_sub_node(node_type) else ""
#     )

#     return (
#         f'Successfully added "{added_node.name}" '
#         f'({added_node.displayName or added_node.type})'
#         f'{sub_node_info} with ID {added_node.id}'
#     )


# def get_custom_node_title(
#     input_data: Dict[str, Any],
#     node_types: List[INodeTypeDescription],
# ) -> str:
#     node_type_name = input_data.get("nodeType")

#     if isinstance(node_type_name, str):
#         node_type = next(
#             (nt for nt in node_types if nt.name == node_type_name),
#             None,
#         )
#         if node_type:
#             return f"Adding {node_type.displayName} node"

#     return "Adding node"


# # ---------------------------------------------------------------------
# # Tool Base
# # ---------------------------------------------------------------------

# def get_add_node_tool_base(
#     node_types: List[INodeTypeDescription],
# ) -> BuilderToolBase:
#     return BuilderToolBase(
#         toolName="add_nodes",
#         displayTitle="Adding nodes",
#         getCustomDisplayTitle=lambda input_data: get_custom_node_title(
#             input_data, node_types
#         ),
#     )


# # ---------------------------------------------------------------------
# # Tool Factory
# # ---------------------------------------------------------------------

# def create_add_node_tool(
#     node_types: List[INodeTypeDescription],
# ) -> BuilderTool:
#     tool_base = get_add_node_tool_base(node_types)

#     @tool()
#     async def add_node_tool(
#         input: Dict[str, Any],
#         config: Dict[str, Any],
#     ):
#         """
#         Docstring for add_node_tool
        
#         :param input: Description
#         :type input: Dict[str, Any]
#         :param config: Description
#         :type config: Dict[str, Any]
#         """ 
#         reporter = createProgressReporter(
#             config=config,
#             tool_name=tool_base.toolName,
#             display_title=tool_base.displayTitle,
#             custom_title=get_custom_node_title(input, node_types),
#         )

#         try:
#             node_id: Optional[str] = None

#             if os.getenv("E2E_TESTS"):
#                 validated = NodeCreationE2ESchema(**input)
#                 node_id = validated.id
#             else:
#                 validated = NodeCreationSchema(**input)

#             reporter.start(validated.dict())

#             state = get_workflow_state()
#             workflow = get_current_workflow(state)

#             reporter.progress(
#                 f"Adding {validated.name} "
#                 f"({validated.connectionParametersReasoning})"
#             )

#             node_type_desc = find_node_type(
#                 validated.nodeType,
#                 validated.nodeVersion,
#                 node_types,
#             )

#             if not node_type_desc:
#                 error = NodeTypeNotFoundError(validated.nodeType)
#                 tool_error: ToolError = {
#                     "message": str(error),
#                     "code": "NODE_TYPE_NOT_FOUND",
#                     "details": {"nodeType": validated.nodeType},
#                 }
#                 reporter.error(tool_error)
#                 return create_error_response(config, tool_error)

#             new_node = create_node(
#                 node_type=node_type_desc,
#                 type_version=validated.nodeVersion,
#                 custom_name=validated.name,
#                 existing_nodes=workflow.nodes,
#                 node_types=node_types,
#                 connection_parameters=validated.connectionParameters,
#                 node_id=node_id,
#             )

#             added_node = AddedNode(
#                 id=new_node.id,
#                 name=new_node.name,
#                 type=new_node.type,
#                 displayName=node_type_desc.displayName,
#                 position=new_node.position,
#                 parameters=new_node.parameters,
#             )

#             message = build_response_message(added_node, node_types)

#             output = AddNodeOutput(
#                 addedNode=added_node,
#                 message=message,
#             )

#             reporter.complete(output.dict())

#             state_updates = add_node_to_workflow(new_node)

#             return create_success_response(
#                 config=config,
#                 message=message,
#                 state_updates=state_updates,
#             )

#         except PydanticValidationError as e:
#             validation_error = ValidationError(
#                 "Invalid input parameters",
#                 details=e.errors(),
#             )

#             tool_error: ToolError = {
#                 "message": validation_error.message,
#                 "code": "VALIDATION_ERROR",
#                 "details": e.errors(),
#             }

#             reporter.error(tool_error)
#             return create_error_response(config, tool_error)

#         except Exception as e:
#             tool_error: ToolError = {
#                 "message": str(e),
#                 "code": "EXECUTION_ERROR",
#             }

#             reporter.error(tool_error)
#             return create_error_response(config, tool_error)

#     return BuilderTool(
#         tool=add_node_tool,
#         **tool_base.__dict__,
#     )



# --------------------Add Node testing code  Implementation-----------------------

# from __future__ import annotations

# import uuid
# from typing import Any, Dict, List, Optional

# from pydantic import BaseModel, Field, ValidationError
# from langchain.tools import Tool


# # =========================================================
# # Errors
# # =========================================================

# class NodeTypeNotFoundError(Exception):
#     def __init__(self, node_type: str):
#         super().__init__(f"Node type '{node_type}' not found")


# class ToolExecutionError(Exception):
#     pass


# # =========================================================
# # Node & Workflow Models (n8n-compatible abstraction)
# # =========================================================

# class NodeTypeDescription:
#     def __init__(self, name: str, display_name: str, is_sub_node: bool = False):
#         self.name = name
#         self.display_name = display_name
#         self.is_sub_node = is_sub_node
#         self.default_name = display_name


# class Node:
#     def __init__(
#         self,
#         node_id: str,
#         node_type: str,
#         name: str,
#         position: List[int],
#         parameters: Dict[str, Any],
#     ):
#         self.id = node_id
#         self.type = node_type
#         self.name = name
#         self.position = position
#         self.parameters = parameters


# class Workflow:
#     def __init__(self):
#         self.nodes: List[Node] = []


# # =========================================================
# # Input Schemas (Zod → Pydantic)
# # =========================================================

# class NodeCreationInput(BaseModel):
#     nodeType: str = Field(..., description="The type of node to add")
#     nodeVersion: int = Field(..., description="Exact node version")
#     name: str = Field(..., description="Human readable node name")
#     connectionParametersReasoning: str = Field(
#         ..., description="Explain reasoning for connection parameters"
#     )
#     connectionParameters: Dict[str, Any] = Field(
#         default_factory=dict,
#         description="Only connection-affecting parameters",
#     )


# class NodeCreationE2EInput(NodeCreationInput):
#     id: Optional[str] = Field(
#         None,
#         description="Optional deterministic node ID for E2E tests",
#     )


# # =========================================================
# # Workflow State Management (Deterministic)
# # =========================================================

# _WORKFLOW_STATE = Workflow()


# def get_workflow_state() -> Workflow:
#     return _WORKFLOW_STATE


# def get_current_workflow(state: Workflow) -> Workflow:
#     return state


# def add_node_to_workflow(node: Node) -> Dict[str, Any]:
#     _WORKFLOW_STATE.nodes.append(node)
#     return {
#         "operation": "add_node",
#         "nodeId": node.id,
#     }


# # =========================================================
# # Utility Functions
# # =========================================================

# def generate_unique_name(base_name: str, existing_nodes: List[Node]) -> str:
#     existing_names = {n.name for n in existing_nodes}
#     if base_name not in existing_names:
#         return base_name

#     i = 1
#     while f"{base_name} {i}" in existing_names:
#         i += 1
#     return f"{base_name} {i}"


# def calculate_node_position(
#     existing_nodes: List[Node],
#     is_sub_node: bool,
#     node_types: List[NodeTypeDescription],
# ) -> List[int]:
#     if not existing_nodes:
#         return [300, 300]

#     last_node = existing_nodes[-1]
#     x_offset = 250 if not is_sub_node else 120
#     return [last_node.position[0] + x_offset, last_node.position[1]]


# def is_sub_node(node_type: NodeTypeDescription) -> bool:
#     return node_type.is_sub_node


# def create_node_instance(
#     node_type_desc: NodeTypeDescription,
#     version: int,
#     name: str,
#     position: List[int],
#     parameters: Dict[str, Any],
#     node_id: Optional[str] = None,
# ) -> Node:
#     return Node(
#         node_id=node_id or str(uuid.uuid4()),
#         node_type=node_type_desc.name,
#         name=name,
#         position=position,
#         parameters=parameters,
#     )


# def find_node_type(
#     node_type: str,
#     version: int,
#     node_types: List[NodeTypeDescription],
# ) -> Optional[NodeTypeDescription]:
#     for nt in node_types:
#         if nt.name == node_type:
#             return nt
#     return None


# # Progress Reporter (UI / Streaming Friendly)


# class ProgressReporter:
#     def __init__(self, tool_name: str, display_title: str, custom_title: str):
#         self.tool_name = tool_name
#         self.display_title = display_title
#         self.custom_title = custom_title

#     def start(self, payload: Dict[str, Any]):
#         pass

#     def progress(self, message: str):
#         pass

#     def complete(self, payload: Dict[str, Any]):
#         pass

#     def error(self, error: Dict[str, Any]):
#         pass


# def create_progress_reporter(
#     config: dict,
#     tool_name: str,
#     display_title: str,
#     custom_title: str,
# ) -> ProgressReporter:
#     return ProgressReporter(tool_name, display_title, custom_title)


# # =========================================================
# # Response Helpers
# # =========================================================

# def create_success_response(config: dict, message: str, state_updates: dict) -> dict:
#     return {
#         "success": True,
#         "message": message,
#         "stateUpdates": state_updates,
#     }


# def create_error_response(config: dict, error: Exception | dict) -> dict:
#     return {
#         "success": False,
#         "error": str(error),
#     }


# # =========================================================
# # Core Node Creation Logic
# # =========================================================

# def create_node(
#     node_type_desc: NodeTypeDescription,
#     node_version: int,
#     custom_name: str,
#     existing_nodes: List[Node],
#     node_types: List[NodeTypeDescription],
#     connection_parameters: Dict[str, Any],
#     node_id: Optional[str],
# ) -> Node:

#     base_name = custom_name or node_type_desc.default_name
#     unique_name = generate_unique_name(base_name, existing_nodes)

#     position = calculate_node_position(
#         existing_nodes,
#         is_sub_node(node_type_desc),
#         node_types,
#     )

#     return create_node_instance(
#         node_type_desc=node_type_desc,
#         version=node_version,
#         name=unique_name,
#         position=position,
#         parameters=connection_parameters,
#         node_id=node_id,
#     )


# def build_response_message(added_node: dict, node_types: List[NodeTypeDescription]) -> str:
#     node_type = next(
#         (nt for nt in node_types if nt.name == added_node["type"]),
#         None,
#     )
#     sub = " (sub-node)" if node_type and node_type.is_sub_node else ""
#     return (
#         f'Successfully added "{added_node["name"]}" '
#         f'({node_type.display_name if node_type else added_node["type"]})'
#         f'{sub} with ID {added_node["id"]}'
#     )


# # =========================================================
# # Tool Factory
# # =========================================================

# def create_add_node_tool(node_types: List[NodeTypeDescription]) -> Tool:

#     def add_node_executor(input_data: dict, config: dict) -> dict:
#         reporter = create_progress_reporter(
#             config,
#             tool_name="add_nodes",
#             display_title="Adding nodes",
#             custom_title="Adding node",
#         )

#         try:
#             # -------- Validation --------
#             if config.get("E2E_TESTS"):
#                 validated = NodeCreationE2EInput(**input_data)
#                 node_id = validated.id
#             else:
#                 validated = NodeCreationInput(**input_data)
#                 node_id = None

#             reporter.start(validated.dict())

#             # -------- State --------
#             state = get_workflow_state()
#             workflow = get_current_workflow(state)

#             reporter.progress(
#                 f"Adding {validated.name} ({validated.connectionParametersReasoning})"
#             )

#             # -------- Node type --------
#             node_type_desc = find_node_type(
#                 validated.nodeType,
#                 validated.nodeVersion,
#                 node_types,
#             )
#             if not node_type_desc:
#                 raise NodeTypeNotFoundError(validated.nodeType)

#             # -------- Node creation --------
#             new_node = create_node(
#                 node_type_desc=node_type_desc,
#                 node_version=validated.nodeVersion,
#                 custom_name=validated.name,
#                 existing_nodes=workflow.nodes,
#                 node_types=node_types,
#                 connection_parameters=validated.connectionParameters,
#                 node_id=node_id,
#             )

#             added_node_info = {
#                 "id": new_node.id,
#                 "name": new_node.name,
#                 "type": new_node.type,
#                 "displayName": node_type_desc.display_name,
#                 "position": new_node.position,
#                 "parameters": new_node.parameters,
#             }

#             message = build_response_message(added_node_info, node_types)

#             reporter.complete({
#                 "addedNode": added_node_info,
#                 "message": message,
#             })

#             state_updates = add_node_to_workflow(new_node)
#             return create_success_response(config, message, state_updates)

#         except ValidationError as ve:
#             reporter.error({"code": "VALIDATION_ERROR", "details": ve.errors()})
#             return create_error_response(config, ve)

#         except Exception as ex:
#             reporter.error({"code": "EXECUTION_ERROR", "message": str(ex)})
#             return create_error_response(config, ex)

#     return Tool(
#         name="add_nodes",
#         description="""
# Add a node to the workflow canvas.

# CRITICAL RULES:
# 1. Always provide connectionParametersReasoning
# 2. Explicitly set connectionParameters (use {} if none)
# 3. Never rely on defaults
# """,
#         func=add_node_executor,
#     )


# --------------------Add Node (Final code ) Implementation-----------------------

from typing import Dict, Any, Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError

from backend.n8n_worflow.inode_type_description import INode, INodeParameters, INodeTypeDescription

from backend.utills.stream_processor import BuilderTool, BuilderToolBase

from backend.error import NodeTypeNotFoundError, ValidationError
from backend.utills.node_creation import create_node_instance, generate_unique_name
from backend.utills.node_positioning import calculate_node_position
from backend.utills.node_helpers import is_sub_node

from backend.mytools.helpers.progress import createProgressReporter
from backend.mytools.helpers.response import create_success_response, create_error_response
from backend.mytools.helpers.state import get_current_workflow, add_node_to_workflow, get_workflow_state
from backend.mytools.helpers.validation import find_node_type

from backend.mytypes.nodes import AddedNode
from backend.mytypes.tools import AddNodeOutput, ToolError

class NodeCreationSchema(BaseModel):
    nodeType: str = Field(description="The type of node to add")
    nodeVersion: int = Field(description="Exact node version")
    name: str = Field(description="Descriptive node name")
    connectionParametersReasoning: str = Field(
        description="REQUIRED: Explain why connection parameters are chosen"
    )
    connectionParameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Only connection-affecting parameters"
    )


class NodeCreationE2ESchema(NodeCreationSchema):
    id: Optional[str] = Field(
        default=None,
        description="Optional deterministic ID (E2E only)"
    )

def create_node(
    node_type: INodeTypeDescription,
    type_version: int,
    custom_name: str,
    existing_nodes: list[INode],
    node_types: list[INodeTypeDescription],
    connection_parameters: Optional[INodeParameters] = None,
    node_id: Optional[str] = None,
) -> INode:

    base_name = custom_name or node_type.defaults.get("name") or node_type.displayName
    unique_name = generate_unique_name(base_name, existing_nodes)

    position = calculate_node_position(
        existing_nodes,
        is_sub_node(node_type),
        node_types
    )

    return create_node_instance(
        node_type=node_type,
        type_version=type_version,
        name=unique_name,
        position=position,
        connection_parameters=connection_parameters,
        node_id=node_id,
    )

def build_response_message(
    added_node: AddedNode,
    node_types: list[INodeTypeDescription],
) -> str:

    node_type = next(
        (nt for nt in node_types if nt.name == added_node.type),
        None,
    )

    sub_node_info = " (sub-node)" if node_type and is_sub_node(node_type) else ""
    return (
        f'Successfully added "{added_node.name}" '
        f'({added_node.displayName or added_node.type})'
        f'{sub_node_info} with ID {added_node.id}'
    )

def get_custom_node_title(
    input_data: Dict[str, Any],
    node_types: list[INodeTypeDescription],
) -> str:

    node_type_name = input_data.get("nodeType")
    if isinstance(node_type_name, str):
        node_type = next(
            (nt for nt in node_types if nt.name == node_type_name),
            None,
        )
        if node_type:
            return f"Adding {node_type.displayName} node"

    return "Adding node"

def get_add_node_tool_base(
    node_types: list[INodeTypeDescription],
) -> BuilderToolBase:

    return BuilderToolBase(
        toolName="add_nodes",
        displayTitle="Adding nodes",
        getCustomDisplayTitle=lambda input_data: get_custom_node_title(
            input_data, node_types
        ),
    )

def create_add_node_tool(
    node_types: list[INodeTypeDescription],
) -> BuilderTool:
    print("Creating add_node_tool with node types:")
    print(node_types)
    builder_tool_base = get_add_node_tool_base(node_types)

    @tool
    async def add_node_tool(payload: Dict[str, Any]):
        """
        Add a node to the workflow canvas.

        Expected payload:
        {
            "input_data": {...},
            "config": {...}
        }
        """
        print("This is the payload received in add_node_tool:", payload)
    
        input_data = payload.get("input_data")
        config = payload.get("config", {})

        print("line 809")

        reporter = createProgressReporter(
            config=config,
            toolName="add_nodes",
            displayTitle="Adding nodes",
            customTitle=get_custom_node_title(input_data, node_types),
        )
        print("line 816")

        try:
            node_id = None
            if config.get("E2E_TESTS"):
                validated = NodeCreationE2ESchema(**input_data)
                node_id = validated.id
            else:
                validated = NodeCreationSchema(**input_data)
            print("line 825")
            reporter.start(validated.dict())

            state = get_workflow_state()
            print("state:", state)
            workflow = get_current_workflow(state)

            reporter.progress(
                f"Adding {validated.name} ({validated.connectionParametersReasoning})"
            )
            print("line 834")
            node_type_desc = find_node_type(
                validated.nodeType,
                validated.nodeVersion,
                node_types,
            )

            if not node_type_desc:
                error = {
                    "message": f"Node type {validated.nodeType} not found",
                    "code": "NODE_TYPE_NOT_FOUND",
                    "details": {"nodeType": validated.nodeType},
                }
                reporter.error(error)
                return create_error_response(config, error)
            print("line 849")
            print(workflow)
            new_node = create_node(
                node_type=node_type_desc,
                type_version=validated.nodeVersion,
                custom_name=validated.name,
                existing_nodes=workflow["nodes"],
                node_types=node_types,
                connection_parameters=validated.connectionParameters,
                node_id=node_id,
            )
            print("line 859")
            added_node = AddedNode(
                id=new_node.id,
                name=new_node.name,
                type=new_node.type,
                displayName=node_type_desc.displayName,
                position=new_node.position,
                parameters=new_node.parameters,
            )

            message = build_response_message(added_node, node_types)
            print("line 870")
            reporter.complete({
                "addedNode": added_node,
                "message": message,
            })

            state_updates = add_node_to_workflow(new_node)
            return create_success_response(config, message, state_updates)

        except Exception as e:
            return create_error_response(
                config,
                {"message": str(e), "code": "EXECUTION_ERROR"},
            )

    return BuilderTool(
        tool=add_node_tool,
        **builder_tool_base.__dict__,
    )
