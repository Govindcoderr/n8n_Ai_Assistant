
from typing import Any, Dict, List, Optional, Union, Literal
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import json

# Constants
MAX_NODE_EXAMPLE_CHARS = 5000 * 4  # Assuming ~4 chars per token like Anthropic 

# Type definitions (equivalent to TypeScript interfaces) 
class NodeParameterValue:
    pass  # Will be defined as Union types

NodeParameterValueType = Union[
    str, int, bool, None, float,
    Dict[str, Any],  # INodeParameters equivalent
    List[Any]  # Arrays
] 

class INodeParameters(Dict[str, NodeParameterValueType]):
    pass

NodePropertyTypes = Literal[
    'boolean', 'button', 'collection', 'color', 'dateTime', 'fixedCollection',
    'hidden', 'json', 'callout', 'notice', 'multiOptions', 'number', 'options',
    'string', 'credentialsSelect', 'resourceLocator', 'curlImport', 'resourceMapper',
    'filter', 'assignmentCollection', 'credentials', 'workflowSelector'
]

class INodeProperties(BaseModel):
    displayName: str
    name: str
    type: NodePropertyTypes
    default: NodeParameterValueType
    description: Optional[str] = None
    required: Optional[bool] = None
    options: Optional[List[Any]] = None

# NodeConnectionType = Literal[
#     'main', 'ai_tool', 'ai_agent', 'ai_memory', 'ai_chain', 'ai_document',
#     'ai_embedding', 'ai_languageModel', 'ai_outputParser', 'ai_retriever',
#     'ai_textSplitter', 'ai_vectorStore', 'NodeConnectionType = str',
# ]

NodeConnectionType = str

class INodeTypeDescription(BaseModel):
    name: str
    displayName: str
    description: str
    version: Union[int, List[int]]
    # properties: List[INodeProperties]
    inputs: Union[List[NodeConnectionType], str]
    outputs: Union[List[NodeConnectionType], str]
    subtitle: Optional[str] = None
    # group: List[str]
    icon: Optional[str] = None

class NodeDetails(BaseModel):
    name: str
    displayName: str
    description: str
    # properties: List[INodeProperties]
    subtitle: Optional[str] = None
    inputs: Union[List[NodeConnectionType], str]
    outputs: Union[List[NodeConnectionType], str]

class NodeDetailsOutput(BaseModel):
    details: NodeDetails
    found: bool
    message: str

# Input schema for the tool
class NodeDetailsInput(BaseModel):
    nodeName: str = Field(description="The exact node type name (e.g., n8n-nodes-base.httpRequest)")
    nodeVersion: int = Field(description="The exact node version")
    withParameters: bool = Field(default=False, description="Whether to include node parameters in the output")
    withConnections: bool = Field(default=True, description="Whether to include node supported connections in the output")

# Helper functions
def format_inputs(inputs: Union[List[NodeConnectionType], str]) -> str:
    """Format node inputs"""
    if not inputs:
        return '<inputs>none</inputs>'
    if isinstance(inputs, str):
        return f'<input>{inputs}</input>'
    formatted_inputs = [f'<input>{json.dumps(input_item)}</input>' for input_item in inputs]
    return '\n'.join(formatted_inputs)

def format_outputs(outputs: Union[List[NodeConnectionType], str]) -> str:
    """Format node outputs"""
    if not outputs:
        return '<outputs>none</outputs>'
    if isinstance(outputs, str):
        return f'<output>{outputs}</output>'
    formatted_outputs = [f'<output>{json.dumps(output_item)}</output>' for output_item in outputs]
    return '\n'.join(formatted_outputs)

def format_node_details(
    details: NodeDetails,
    with_parameters: bool = False,
    with_connections: bool = True,
    examples: Optional[List[INodeParameters]] = None,
) -> str:
    """Format node details into a structured message"""
    parts = []

    # Basic details
    parts.append('<node_details>')
    parts.append(f'<name>{details.name}</name>')
    parts.append(f'<display_name>{details.displayName}</display_name>')
    parts.append(f'<description>{details.description}</description>')

    if details.subtitle:
        parts.append(f'<subtitle>{details.subtitle}</subtitle>')

    # Parameters
    # if with_parameters and details.properties:
    #     stringified_properties = json.dumps([prop.dict() for prop in details.properties], indent=2)
    #     if len(stringified_properties) > 1000:
    #         truncated = stringified_properties[:1000] + '... Rest of properties omitted'
    #     else:
    #         truncated = stringified_properties
    #     parts.append(f'<properties>\n{truncated}\n</properties>')

    # Connections
    if with_connections:
        parts.append('<connections>')
        parts.append(format_inputs(details.inputs))
        parts.append(format_outputs(details.outputs))
        parts.append('</connections>')

    # Example configurations from workflow examples (with token limit)
    if examples:
        example_parts = []
        chars_used = 0
        for example in examples:
            example_str = json.dumps(example, indent=2)
            if chars_used + len(example_str) <= MAX_NODE_EXAMPLE_CHARS:
                example_parts.append(example_str)
                chars_used += len(example_str)

        if example_parts:
            parts.append('<node_examples>')
            parts.extend(example_parts)
            parts.append('</node_examples>')

    parts.append('</node_details>')

    return '\n'.join(parts)

def extract_node_details(node_type: INodeTypeDescription) -> NodeDetails:
    """Helper to extract node details from a node type description"""
    return NodeDetails(
        name=node_type.name,
        displayName=node_type.displayName,
        description=node_type.description,
        # properties=node_type.properties,
        subtitle=node_type.subtitle,
        inputs=node_type.inputs,
        outputs=node_type.outputs,
    )

def find_node_type(
    node_name: str,
    node_version: int,
    node_types: List[INodeTypeDescription]
) -> Optional[INodeTypeDescription]:
    """Find a node type by name and version"""
    for node_type in node_types:
        if node_type.name == node_name:
            if isinstance(node_type.version, list):
                if node_version in node_type.version:
                    return node_type
            elif node_type.version == node_version:
                return node_type
    return None

# Tool configuration
TOOL_NAME = 'get_node_details'
DISPLAY_TITLE = 'Getting node details'

class ValidationError(Exception):
    pass

class ToolExecutionError(Exception):
    pass

# Mock progress reporter (simplified for Python)
class ProgressReporter:
    def start(self, input_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None):
        pass

    def progress(self, message: str, data: Optional[Dict[str, Any]] = None):
        pass

    def complete(self, output: Any):
        pass

    def error(self, error: Exception):
        pass

def create_progress_reporter(config: Any, tool_name: str, display_title: str) -> ProgressReporter:
    return ProgressReporter()

def report_progress(reporter: ProgressReporter, message: str):
    reporter.progress(message)

def create_success_response(config: Any, message: str) -> Dict[str, Any]:
    return {"success": True, "message": message}

def create_error_response(config: Any, error: Exception) -> Dict[str, Any]:
    return {"success": False, "error": str(error)}

def get_workflow_state() -> Optional[Dict[str, Any]]:
    """Mock function to get workflow state - implement based on your needs"""
    # This would need to be implemented based on your Python environment
    
    return None

def create_node_details_tool(node_types: List[INodeTypeDescription]):
    """Factory function to create the node details tool"""

    @tool(TOOL_NAME)
    def get_node_details(
        nodeName: str,
        nodeVersion: int,
        withParameters: bool = False,
        withConnections: bool = True
    ) -> str:
        """
        Get detailed information about a specific  node type including properties and available connections.
        Use this before adding nodes to understand their input/output structure.

        Args:
            nodeName: The exact node type name (e.g., n8n-nodes-base.httpRequest)
            nodeVersion: The exact node version
            withParameters: Whether to include node parameters in the output
            withConnections: Whether to include node supported connections in the output
        """
        # Create progress reporter (mock implementation)
        reporter = create_progress_reporter(None, TOOL_NAME, DISPLAY_TITLE)

        try:
            # Validate input using Pydantic
            input_data = NodeDetailsInput(
                nodeName=nodeName,
                nodeVersion=nodeVersion,
                withParameters=withParameters,
                withConnections=withConnections
            )

            # Report tool start
            reporter.start(input_data.dict())

            # Report progress
            report_progress(reporter, f"Looking up details for {nodeName}...")

            # Find the node type
            node_type = find_node_type(nodeName, nodeVersion, node_types)

            if not node_type:
                error_msg = f"Node type '{nodeName}' with version {nodeVersion} not found"
                reporter.error(ValueError(error_msg))
                return create_error_response(None, ValueError(error_msg))["error"]

            # Extract node details
            details = extract_node_details(node_type)

            # Get example configurations from state, filtered by node type and version
            examples = []
            try:
                state = get_workflow_state()
                if state and 'nodeConfigurations' in state:
                    all_node_configs = state['nodeConfigurations'].get(nodeName, [])
                    examples = [
                        config['parameters']
                        for config in all_node_configs
                        if config.get('version') == nodeVersion
                    ]
            except Exception:
                # State may not be available in test environments
                examples = []

            # Format the output message with examples
            message = format_node_details(details, withParameters, withConnections, examples)

            # Report completion
            output = NodeDetailsOutput(
                details=details,
                found=True,
                message=message
            )
            reporter.complete(output)

            # Return success response
            return create_success_response(None, message)["message"]

        except Exception as error:
            # Handle validation or unexpected errors
            if isinstance(error, ValidationError):
                reporter.error(error)
                return create_error_response(None, error)["error"]

            tool_error = ToolExecutionError(f"Unknown error occurred: {str(error)}")
            reporter.error(tool_error)
            return create_error_response(None, tool_error)["error"]

    return {
        "tool": get_node_details,
        "tool_name": TOOL_NAME,
        "display_title": DISPLAY_TITLE,
    }

# # Example usage:
# if __name__ == "__main__":
#     # Example node types (you would load these from your n8n instance)
#     sample_node_types = [
#         INodeTypeDescription(
#             name="n8n-nodes-base.httpRequest",
#             displayName="HTTP Request",
#             description="Makes an HTTP request and returns the response data",
#             version=1,
#             properties=[
#                 INodeProperties(
#                     displayName="Method",
#                     name="method",
#                     type="options",
#                     default="GET",
#                     options=[
#                         {"name": "GET", "value": "GET"},
#                         {"name": "POST", "value": "POST"}
#                     ]
#                 )
#             ],
#             inputs=["main"],
#             outputs=["main"],
#             subtitle="GET, POST, PUT, etc.",
#             group=["input"],
#             icon="fa:globe"
#         )
#     ]

#     # Create the tool
#     tool_config = create_node_details_tool(sample_node_types)
#     tool = tool_config["tool"]

#     # Test the tool
#     result = tool.invoke({
#         "nodeName": "n8n-nodes-base.httpRequest",
#         "nodeVersion": 1,
#         "withParameters": True,
#         "withConnections": True
#     })

#     print("Tool Result:")
#     print(result)
