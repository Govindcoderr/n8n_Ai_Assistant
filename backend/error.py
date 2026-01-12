# class ToolExecutionError(Exception):
#     def __init__(self, message: str, tool_name: str | None = None, cause=None):
#         super().__init__(message)
#         self.tool_name = tool_name
#         self.cause = cause
#         self.message = message  

class ToolError(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        details: dict | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

class ToolExecutionError(ToolError):
    def __init__(
        self,
        message: str,
        tool_name: str | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(
            message=message,
            code="TOOL_EXECUTION_ERROR",
            details={
                "toolName": tool_name,
                "cause": repr(cause) if cause else None,
            },
        )
        self.tool_name = tool_name
        self.cause = cause


class ValidationError(Exception):
    def __init__(self, message: str, extra: dict | None = None):
        super().__init__(message)
        self.extra = extra or {}
