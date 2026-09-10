"""Domain errors are independent of the MCP SDK."""


class ProjectError(Exception):
    def __init__(self, code: str, message: str, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


def require(condition: bool, message: str, code: str = "invalid_project") -> None:
    if not condition:
        raise ProjectError(code, message)
