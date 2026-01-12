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
