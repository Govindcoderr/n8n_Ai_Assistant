
from typing import List, Dict, Any, Optional
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, ValidationError as PydanticValidationError

from backend.utills.stream_processor import BuilderToolBase
from backend.error import ValidationError, ToolExecutionError
from backend.mytools.engine.node_search_engine import NodeSearchEngine
    
from backend.mytools.helpers.progress import createProgressReporter, createBatchProgressReporter
from backend.mytools.helpers.response import create_success_response, create_error_response         
from backend.mytypes.tools import NodeSearchOutput

class SearchQuery(BaseModel):
    queryType: str
    query: Optional[str] = None
    connectionType: Optional[str] = None
    subNodeSearch: Optional[bool] = False


class NodeSearchSchema(BaseModel):
    queries: List[SearchQuery]

NODE_SEARCH_TOOL: BuilderToolBase = {
    "toolName": "search_nodes",
    "displayTitle": "Searching nodes",
}

SEARCH_LIMIT = 5
def create_node_search_tool(node_types: List[Dict[str, Any]]):
 
    def tool(**kwargs):
        input_data = NodeSearchSchema(**kwargs)
        """
        NOTE:
        - LangChain Python passes ONLY input    
        - No config argument is injected automatically
        """

        config: Dict[str, Any] = {}

        reporter = createProgressReporter(
            config,
            NODE_SEARCH_TOOL["toolName"],
            NODE_SEARCH_TOOL["displayTitle"],
        )

        try:
            reporter.start(input_data.dict())

            engine = NodeSearchEngine(node_types)

            batch = createBatchProgressReporter(reporter, "Searching nodes")
            batch.init(len(input_data.queries))

            all_results = []

            for q in input_data.queries:
                if q.queryType == "name":
                    results = engine.search_by_name(q.query or "", SEARCH_LIMIT)
                    identifier = q.query or ""
                else:
                    results = engine.search_by_connection_type(
                        q.connectionType,
                        SEARCH_LIMIT,
                        q.query,
                    )
                    identifier = f"sub-nodes with {q.connectionType}"

                batch.next(identifier)
                all_results.append({
                    "query": identifier,
                    "results": results,
                })

            batch.complete()

            output: NodeSearchOutput = {
                "results": all_results,
                "totalResults": sum(len(r["results"]) for r in all_results),
                "message": "Node search completed",
            }

            reporter.complete(output)
            return create_success_response(output["message"], output)

        except PydanticValidationError as e:
            err = ValidationError(
                "Invalid input parameters",
                extra={"errors": e.errors()},
            )
            reporter.error(err)
            return create_error_response(err)

        except Exception as e:
            err = ToolExecutionError(
                str(e),
                tool_name=NODE_SEARCH_TOOL["toolName"],
                cause=e,
            )
            reporter.error(err)
            return create_error_response(err)

    return {
        "tool": StructuredTool.from_function(
            func=tool,
            name=NODE_SEARCH_TOOL["toolName"],
            description="Search n8n nodes by name or connection type",
            args_schema=NodeSearchSchema,
        ),
        **NODE_SEARCH_TOOL,
    }





# from typing import List, Dict, Any, Optional
# from langchain_core.tools import StructuredTool
# from pydantic import BaseModel, ValidationError as PydanticValidationError

# from backend.error import ValidationError, ToolExecutionError
# from backend.mytools.engine.node_search_engine import NodeSearchEngine
# from backend.mytools.helpers.progress import createProgressReporter, createBatchProgressReporter
# from backend.mytools.helpers.response import create_success_response, create_error_response
# from backend.mytypes.tools import NodeSearchOutput

# # Input Schemas (Zod → Pydantic equivalent)
# class SearchQuery(BaseModel):
#     queryType: str  # "name" | "subNodeSearch"
#     query: Optional[str] = None
#     connectionType: Optional[str] = None


# class NodeSearchInput(BaseModel):
#     queries: List[SearchQuery]

# # Tool Metadata and Constants
# NODE_SEARCH_TOOL = {
#     "toolName": "search_nodes",
#     "displayTitle": "Searching nodes",
# }

# SEARCH_LIMIT = 5

# # Factory function (same name, same behavior)
# def create_node_search_tool(node_types: List[Dict[str, Any]]):

#     def _tool(**kwargs):
#         input = NodeSearchInput(**kwargs)
#         """
#         NOTE:
#         - LangChain Python passes ONLY input
#         - No config argument is injected automatically
#         """

#         # Dummy config for reporter (safe default)
#         config: Dict[str, Any] = {}

#         reporter = createProgressReporter(
#             config,
#             NODE_SEARCH_TOOL["toolName"],
#             NODE_SEARCH_TOOL["displayTitle"],
#         )

#         try:
#             reporter.start(input.dict())

#             search_engine = NodeSearchEngine(node_types)

#             batch = createBatchProgressReporter(reporter, "Searching nodes")
#             batch.init(len(input.queries))

#             all_results = []

#             for q in input.queries:
#                 if q.queryType == "name":
#                     search_results = search_engine.search_by_name(
#                         q.query or "", SEARCH_LIMIT
#                     )
#                     identifier = q.query or ""
#                 else:
#                     search_results = search_engine.search_by_connection_type(
#                         q.connectionType,
#                         SEARCH_LIMIT,
#                         q.query,
#                     )
#                     identifier = (
#                         f'sub-nodes with {q.connectionType} output matching "{q.query}"'
#                         if q.query
#                         else f"sub-nodes with {q.connectionType} output"
#                     )

#                 batch.next(identifier)

#                 all_results.append({
#                     "query": identifier,
#                     "results": search_results,
#                 })

#             batch.complete()

#             # Build response message (same semantics)
#             message_parts = []
#             for r in all_results:
#                 if not r["results"]:
#                     message_parts.append(f'No nodes found matching "{r["query"]}"')
#                 else:
#                     message_parts.append(
#                         f'Found {len(r["results"])} nodes matching "{r["query"]}"'
#                     )

#             response_message = "\n\n".join(message_parts)

#             output: NodeSearchOutput = {
#                 "results": all_results,
#                 "totalResults": sum(len(r["results"]) for r in all_results),
#                 "message": response_message,
#             }

#             reporter.complete(output)

#             return create_success_response(config, response_message)
        

#         except PydanticValidationError as e:
#             err = ValidationError(
#                 "Invalid input parameters",
#                 extra={"errors": e.errors()},
#             )
#             reporter.error(err)
#             return create_error_response(config, err)

#         except Exception as e:
#             err = ToolExecutionError(
#                 message=str(e),
#                 tool_name=NODE_SEARCH_TOOL["toolName"],
#                 cause=e,
#             )
#             reporter.error(err)
#             return create_error_response(config, err)

#     # StructuredTool (LangChain)
#     return {
#         "tool": StructuredTool.from_function(
#             func=_tool,
#             name=NODE_SEARCH_TOOL["toolName"],
#             description=(
#                 "Search for n8n nodes by name or find sub-nodes that output "
#                 "specific connection types. Use this before adding nodes."
#             ),
#             args_schema=NodeSearchInput,
#         ),
#         **NODE_SEARCH_TOOL,
#     }




