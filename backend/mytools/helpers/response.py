def create_success_response(message: str, data: dict):
    return {
        "status": "success",
        "message": message,
        "data": data,
    }


def create_error_response(error: Exception, config=None):
    return {
        "status": "error",
        "message": str(error),
        "details": getattr(error, "__dict__", {}),
        "config": config,
    }




# from typing import Any, Dict, Optional, TypeVar, Union
# from langchain_core.messages import ToolMessage
# from langchain_core.runnables import RunnableConfig

# # Assuming these are your custom types (you'll need to define them)
# from error import ToolError, StateUpdater, WorkflowState  # ← adjust impo

# TState = TypeVar("TState", bound=WorkflowState)  # Generic state type


# class Command:
#     """
#     Simple command-like return type (similar to LangGraph/Command pattern)
#     In real LangGraph Python you would usually return dict/update directly,
#     but we're mimicking the TS structure here
#     """
#     def __init__(self, update: Dict[str, Any]):
#         self.update = update


# def create_success_response(
#     config: RunnableConfig,
#     message: str,
#     state_updates: Optional[StateUpdater[TState]] = None,
# ) -> Command:
#     """
#     Create a success response with optional state updates
#     """
#     # In Python LangChain, tool_call_id is usually found in config['configurable']
#     # but we try to follow the TS pattern as closely as possible
#     tool_call_id = config.get("tool_call_id") or config["configurable"].get("tool_call_id")

#     if not tool_call_id:
#         raise ValueError("tool_call_id not found in config")

#     tool_message = ToolMessage(
#         content=message,
#         tool_call_id=tool_call_id,
#         name=config.get("name")  # tool name - might be in different place depending on version
#     )

#     update: Dict[str, Any] = {
#         "messages": [tool_message]
#     }

#     if state_updates is not None:
#         # StateUpdater is expected to be dict-like or callable
#         if callable(state_updates):
#             # If it's a function that takes current state
#             update.update(state_updates)  # ← most common pattern in Python
#         else:
#             # If it's already a dict of updates
#             update.update(state_updates)

#     return Command(update=update)


# def create_error_response(
#     config: RunnableConfig,
#     error: ToolError
# ) -> Command:
#     """
#     Create an error response
#     """
#     tool_call_id = config.get("tool_call_id") or config["configurable"].get("tool_call_id")

#     if not tool_call_id:
#         raise ValueError("tool_call_id not found in config")

#     error_message = f"Error: {error.message}"

#     tool_message = ToolMessage(
#         content=error_message,
#         tool_call_id=tool_call_id,
#         name=config.get("name")
#     )

#     return Command(update={
#         "messages": [tool_message]
#     })



# # More realistic LangGraph-style Python version (recommended in practice)


# def create_success_response_modern(
#     config: RunnableConfig,
#     message: str,
#     state_updates: Optional[Dict] = None,
# ) -> Dict:
#     """More pythonic/LangGraph style - just return the update dict"""
#     tool_call_id = (
#         config.get("tool_call_id")
#         or config.get("configurable", {}).get("tool_call_id")
#     )

#     return {
#         "messages": [
#             ToolMessage(
#                 content=message,
#                 tool_call_id=tool_call_id,
#                 name=config.get("name")
#             )
#         ],
#         **(state_updates or {})
#     }


# def create_error_response_modern(
#     config: RunnableConfig,
#     error: Union[Exception, ToolError, str]
# ) -> Dict:
#     """Modern pythonic version"""
#     tool_call_id = (
#         config.get("tool_call_id")
#         or config.get("configurable", {}).get("tool_call_id")
#     )

#     content = f"Error: {getattr(error, 'message', str(error))}"

#     return {
#         "messages": [
#             ToolMessage(
#                 content=content,
#                 tool_call_id=tool_call_id,
#                 name=config.get("name")
#             )
#         ]
#     }

