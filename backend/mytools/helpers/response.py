def create_success_response(message: str, data: dict):
    return {
        "status": "success",
        "message": message,
        "data": data,
    }


def create_error_response(error: Exception):
    return {
        "status": "error",
        "message": str(error),
        "details": getattr(error, "__dict__", {}),
    }
