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

