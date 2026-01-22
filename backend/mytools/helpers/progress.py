# class ProgressReporter:
#     def __init__(self, tool_name: str, display_title: str):
#         self.tool_name = tool_name
#         self.display_title = display_title

#     def start(self, payload):
#         print(f"[{self.display_title}] Started:", payload)

#     def progress(self, message: str):
#         print(f"[{self.display_title}] {message}")

#     def complete(self, output):
#         print(f"[{self.display_title}] Completed:", output)

#     def error(self, error: Exception):
#         print(f"[{self.display_title}] Error:", str(error))


# def create_progress_reporter(tool_name: str, display_title: str):
#     return ProgressReporter(tool_name, display_title)






# Progress reporter implementation

from typing import Any, Dict, Optional, TypeVar

from backend.mytypes.tools import (
    ToolProgressMessage,
    ToolError,
    ProgressReporter,
    BatchReporter,
)

T = TypeVar("T")
TToolName = TypeVar("TToolName", bound=str)

# config: Dict[str, Any]

def createProgressReporter(
    toolName: TToolName,
    displayTitle: str,
    config: Optional[Any] = None,
    customTitle: Optional[str] = None,
) -> ProgressReporter:
    toolCallId = None
    if config and getattr(config, "toolCall", None):
     toolCallId = config.toolCall.get("id")
    

    customDisplayTitle = customTitle
    
    def emit(message: ToolProgressMessage) -> None:
        if config and getattr(config, "writer", None):
            config.writer(message)

    def start(input: T, options: Optional[Dict[str, str]] = None) -> None:
        nonlocal customDisplayTitle
        if options and "customDisplayTitle" in options:
            customDisplayTitle = options["customDisplayTitle"]

        emit({
            "type": "tool",
            "toolName": toolName,
            "toolCallId": toolCallId,
            "displayTitle": displayTitle,
            "customDisplayTitle": customDisplayTitle,
            "status": "running",
            "updates": [
                {
                    "type": "input",
                    "data": input,
                }
            ],
        })

    def progress(message: str, data: Optional[Dict[str, Any]] = None) -> None:
        emit({
            "type": "tool",
            "toolName": toolName,
            "toolCallId": toolCallId,
            "displayTitle": displayTitle,
            "customDisplayTitle": customDisplayTitle,
            "status": "running",
            "updates": [
                {
                    "type": "progress",
                    "data": data if data is not None else {"message": message},
                }
            ],
        })

    def complete(output: T) -> None:
        emit({
            "type": "tool",
            "toolName": toolName,
            "toolCallId": toolCallId,
            "displayTitle": displayTitle,
            "customDisplayTitle": customDisplayTitle,
            "status": "completed",
            "updates": [
                {
                    "type": "output",
                    "data": output,
                }
            ],
        })

    def error(err: ToolError) -> None:
        emit({
            "type": "tool",
            "toolName": toolName,
            "toolCallId": toolCallId,
            "displayTitle": displayTitle,
            "customDisplayTitle": customDisplayTitle,
            "status": "error",
            "updates": [
                {
                    "type": "error",
                    "data": {
                        "message": err.message,
                        "code": err.code,
                        "details": err.details,
                    },
                }
            ],
        })

    def createBatchReporter(scope: str) -> BatchReporter:
        currentIndex = 0
        totalItems = 0

        def init(total: int) -> None:
            nonlocal totalItems, currentIndex
            totalItems = total
            currentIndex = 0

        def next(itemDescription: str) -> None:
            nonlocal currentIndex
            currentIndex += 1
            progress(
                f"{scope}: Processing item {currentIndex} of {totalItems}: {itemDescription}"
            )

        def complete_batch() -> None:
            progress(f"{scope}: Completed all {totalItems} items")

        return BatchReporter(
            init=init,
            next=next,
            complete=complete_batch,
        )

    return ProgressReporter(
        start=start,
        progress=progress,
        complete=complete,
        error=error,
        createBatchReporter=createBatchReporter,
    )

# Helper functions (same names, same behavior)
def reportStart(reporter: ProgressReporter, input: T) -> None:
    reporter.start(input)


def reportProgress(
    reporter: ProgressReporter,
    message: str,
    data: Optional[Dict[str, Any]] = None,
) -> None:
    reporter.progress(message, data)


def reportComplete(reporter: ProgressReporter, output: T) -> None:
    reporter.complete(output)


def reportError(reporter: ProgressReporter, error: ToolError) -> None:
    reporter.error(error)


def createBatchProgressReporter(
    reporter: ProgressReporter,
    scope: str,
) -> BatchReporter:
    return reporter.createBatchReporter(scope)












# from typing import Any, Callable, Dict, Generic, Optional, TypeVar, Union
# from dataclasses import dataclass

# from langchain_core.runnables import RunnableConfig

# # Assume these are defined in your project
# from error import ToolProgressMessage, ToolError  # adjust import path

# T = TypeVar("T")
# TToolName = TypeVar("TToolName", bound=str)


# @dataclass
# class ProgressUpdate:
#     type: str                   # "input" | "progress" | "output" | "error"
#     data: Dict[str, Any]


# @dataclass
# class ToolProgress:
#     type: str = "tool"
#     tool_name: str
#     tool_call_id: Optional[str]
#     display_title: str
#     custom_display_title: Optional[str] = None
#     status: str = "running"     # "running" | "completed" | "error"
#     updates: list[ProgressUpdate] = None

#     def __post_init__(self):
#         if self.updates is None:
#             self.updates = []


# class ProgressReporter(Generic[TToolName]):
#     """
#     Progress reporter for tool execution - Python version
#     """

#     def __init__(
#         self,
#         config: RunnableConfig,
#         tool_name: str,
#         display_title: str,
#         custom_title: Optional[str] = None,
#     ):
#         self.tool_name = tool_name
#         self.display_title = display_title
#         self.custom_display_title = custom_title

#         # Usually found in configurable or directly in config
#         self.tool_call_id = (
#             config.get("tool_call_id")
#             or config.get("configurable", {}).get("tool_call_id")
#         )

#         self.writer: Optional[Callable[[ToolProgressMessage], None]] = config.get("writer")

#     def _emit(self, status: str, update_type: str, data: Dict[str, Any]) -> None:
#         """Internal emit helper"""
#         if self.writer is None:
#             return

#         message = ToolProgress(
#             tool_name=self.tool_name,
#             tool_call_id=self.tool_call_id,
#             display_title=self.display_title,
#             custom_display_title=self.custom_display_title,
#             status=status,
#             updates=[ProgressUpdate(type=update_type, data=data)],
#         )

#         self.writer(message)  # type: ignore

#     def start(self, input_data: Any, *, custom_display_title: Optional[str] = None) -> None:
#         if custom_display_title is not None:
#             self.custom_display_title = custom_display_title

#         self._emit(
#             status="running",
#             update_type="input",
#             data=input_data if isinstance(input_data, dict) else {"input": input_data},
#         )

#     def progress(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
#         payload = data or {}
#         payload.setdefault("message", message)

#         self._emit("running", "progress", payload)

#     def complete(self, output: Any) -> None:
#         self._emit(
#             status="completed",
#             update_type="output",
#             data=output if isinstance(output, dict) else {"output": output},
#         )

#     def error(self, error: Union[Exception, ToolError, str]) -> None:
#         if isinstance(error, Exception):
#             err_data = {
#                 "message": str(error),
#                 "code": getattr(error, "code", None),
#                 "details": getattr(error, "details", None),
#             }
#         elif isinstance(error, str):
#             err_data = {"message": error}
#         else:  # ToolError
#             err_data = {
#                 "message": error.message,
#                 "code": getattr(error, "code", None),
#                 "details": getattr(error, "details", None),
#             }

#         self._emit("error", "error", err_data)

#     def create_batch_reporter(self, scope: str) -> 'BatchProgressReporter':
#         return BatchProgressReporter(self, scope)


# class BatchProgressReporter:
#     """Helper for reporting progress over multiple items"""

#     def __init__(self, reporter: ProgressReporter, scope: str):
#         self.reporter = reporter
#         self.scope = scope
#         self.current_index = 0
#         self.total_items = 0

#     def init(self, total: int) -> None:
#         self.total_items = total
#         self.current_index = 0

#     def next(self, item_description: str) -> None:
#         self.current_index += 1
#         self.reporter.progress(
#             f"{self.scope}: Processing item {self.current_index} of {self.total_items}: {item_description}"
#         )

#     def complete(self) -> None:
#         self.reporter.progress(
#             f"{self.scope}: Completed all {self.total_items} items"
#         )


# # ──── Convenience helper functions ─────────────────────────────────────────────

# def report_start(reporter: ProgressReporter, input_data: Any) -> None:
#     reporter.start(input_data)


# def report_progress(
#     reporter: ProgressReporter, message: str, data: Optional[Dict[str, Any]] = None
# ) -> None:
#     reporter.progress(message, data)


# def report_complete(reporter: ProgressReporter, output: Any) -> None:
#     reporter.complete(output)


# def report_error(reporter: ProgressReporter, error: Union[Exception, ToolError, str]) -> None:
#     reporter.error(error)


# def create_batch_progress_reporter(
#     reporter: ProgressReporter, scope: str
# ) -> BatchProgressReporter:
#     return reporter.create_batch_reporter(scope)


# # ──── Modern / recommended usage example ───────────────────────────────────────

# """
# reporter = ProgressReporter(
#     config,
#     tool_name="search_nodes",
#     display_title="Searching for nodes",
#     custom_title="Finding OpenAI related nodes"
# )

# reporter.start({"query": "openai"})
# reporter.progress("Querying vector store...")
# reporter.complete({"found": 42, "nodes": [...]})
# # or
# reporter.error(ValueError("Database timeout"))

# # Batch example
# batch = create_batch_progress_reporter(reporter, "Page processing")
# batch.init(25)
# for page in pages:
#     batch.next(page.title)
# batch.complete()
# """