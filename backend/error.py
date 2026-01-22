# class ToolExecutionError(Exception):
#     def __init__(self, message: str, tool_name: str | None = None, cause=None):
#         super().__init__(message)
#         self.tool_name = tool_name
#         self.cause = cause
#         self.message = message  

# class ToolError(Exception):
#     def __init__(
#         self,
#         message: str,
#         code: str,
#         details: dict | None = None,
#     ):
#         super().__init__(message)
#         self.message = message
#         self.code = code
#         self.details = details or {}

# class ToolExecutionError(ToolError):
#     def __init__(
#         self,
#         message: str,
#         tool_name: str | None = None,
#         cause: Exception | None = None,
#     ):
#         super().__init__(
#             message=message,
#             code="TOOL_EXECUTION_ERROR",
#             details={
#                 "toolName": tool_name,
#                 "cause": repr(cause) if cause else None,
#             },
#         )
#         self.tool_name = tool_name
#         self.cause = cause


# class ValidationError(Exception):
#     def __init__(self, message: str, extra: dict | None = None):
#         super().__init__(message)
#         self.extra = extra or {}






# new code ends here 
from typing import Any, Dict, Optional


class WorkflowBuilderBaseError(Exception):
    """
    Base class for structured errors in the workflow builder.
    Contains common fields: message, code, details, status_code.
    """
    def __init__(
        self,
        message: str,
        code: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary (useful for JSON/API responses)"""
        return {
            "error": True,
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


# ─── Tool-related errors (kept original names you are already using) ────────

class ToolError(WorkflowBuilderBaseError):
    """Base class for errors that occur during tool execution."""
    pass


class ToolExecutionError(ToolError):
    """
    Raised when a tool fails during execution (unexpected error, timeout, etc.)
    """
    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        cause: Optional[Exception] = None,
    ):
        details = {
            "toolName": tool_name,
            "cause": repr(cause) if cause else None,
            "cause_type": type(cause).__name__ if cause else None,
        }

        super().__init__(
            message=message or "Tool execution failed",
            code="TOOL_EXECUTION_ERROR",
            details=details,
            status_code=500,
        )
        self.tool_name = tool_name
        self.cause = cause


class ValidationError(WorkflowBuilderBaseError):
    """Raised when input/tool parameters fail validation."""
    def __init__(
        self,
        message: str = "Invalid input parameters",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details=details,
            status_code=422,
        )


# ─── Domain-specific errors ──────────────────────────────────────────────────

class NodeNotFoundError(WorkflowBuilderBaseError):
    """Raised when a requested node is not found in the workflow."""
    def __init__(
        self,
        node_identifier: str,
        message: Optional[str] = None,
    ):
        msg = message or f"Node not found: {node_identifier}"
        super().__init__(
            message=msg,
            code="NODE_NOT_FOUND",
            details={"nodeIdentifier": node_identifier},
            status_code=404,
        )


class NodeTypeNotFoundError(WorkflowBuilderBaseError):
    """Raised when requested node type doesn't exist or version mismatch."""
    def __init__(
        self,
        node_type_name: str,
        message: Optional[str] = None,
    ):
        msg = message or f"Node type not found: {node_type_name}"
        super().__init__(
            message=msg,
            code="NODE_TYPE_NOT_FOUND",
            details={"nodeTypeName": node_type_name},
            status_code=404,
        )


class ConnectionError(WorkflowBuilderBaseError):
    """Raised when an invalid connection is attempted."""
    def __init__(
        self,
        message: str = "Invalid connection attempt",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            code="CONNECTION_ERROR",
            details=details,
            status_code=400,
        )


class ParameterTooLargeError(WorkflowBuilderBaseError):
    """Raised when a parameter value exceeds allowed size/limits."""
    def __init__(
        self,
        message: str = "Parameter value is too large",
        parameter: Optional[str] = None,
        node_id: Optional[str] = None,
        max_size: Optional[int] = None,
    ):
        details = {}
        if parameter is not None:
            details["parameter"] = parameter
        if node_id is not None:
            details["nodeId"] = node_id
        if max_size is not None:
            details["maxSize"] = max_size

        super().__init__(
            message=message,
            code="PARAMETER_TOO_LARGE",
            details=details,
            status_code=413,  # Request Entity Too Large
        )


# ─── Utility function for consistent error formatting ────────────────────────

def format_error_response(error: Exception) -> Dict[str, Any]:
    """
    Convert any exception to a consistent API-friendly error response.
    Works best with WorkflowBuilderBaseError subclasses.
    """
    if isinstance(error, WorkflowBuilderBaseError):
        return error.to_dict()

    # Fallback for unexpected/unhandled exceptions
    return {
        "error": True,
        "code": "INTERNAL_SERVER_ERROR",
        "message": str(error),
        "details": {
            "exception_type": type(error).__name__,
            "exception_repr": repr(error),
        },
    } 