class ProgressReporter:
    def __init__(self, tool_name: str, display_title: str):
        self.tool_name = tool_name
        self.display_title = display_title

    def start(self, payload):
        print(f"[{self.display_title}] Started:", payload)

    def progress(self, message: str):
        print(f"[{self.display_title}] {message}")

    def complete(self, output):
        print(f"[{self.display_title}] Completed:", output)

    def error(self, error: Exception):
        print(f"[{self.display_title}] Error:", str(error))


def create_progress_reporter(tool_name: str, display_title: str):
    return ProgressReporter(tool_name, display_title)
