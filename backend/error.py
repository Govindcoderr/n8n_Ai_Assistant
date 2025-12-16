class ToolExecutionError(Exception):
    def __init__(self, message: str, tool_name: str | None = None, cause=None):
        super().__init__(message)
        self.tool_name = tool_name
        self.cause = cause


class ValidationError(Exception):
    def __init__(self, message: str, extra: dict | None = None):
        super().__init__(message)
        self.extra = extra or {}
