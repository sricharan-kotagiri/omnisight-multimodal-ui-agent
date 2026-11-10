"""
Custom exception hierarchy for OmniSight.

All application-specific exceptions inherit from OmniSightException so that
a single FastAPI exception handler can translate them to structured HTTP responses.
"""


class OmniSightException(Exception):
    """Base exception for all OmniSight errors."""

    def __init__(self, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class TaskNotFoundException(OmniSightException):
    """Raised when a requested task does not exist in the database."""

    def __init__(self, task_id: str | None = None) -> None:
        msg = f"Task not found: {task_id}" if task_id else "Task not found"
        super().__init__(message=msg, status_code=404)


class ExecutionNotFoundException(OmniSightException):
    """Raised when a requested execution record does not exist."""

    def __init__(self, execution_id: str | None = None) -> None:
        msg = f"Execution not found: {execution_id}" if execution_id else "Execution not found"
        super().__init__(message=msg, status_code=404)


class ValidationError(OmniSightException):
    """Raised when request data fails business-level validation."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=422)


class BrowserException(OmniSightException):
    """Raised when Playwright encounters an unrecoverable browser error."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=500)


class AIException(OmniSightException):
    """Raised when the Gemini API call fails or returns an unparseable response."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=502)


class HealingException(OmniSightException):
    """Raised when the self-healing engine encounters an internal error."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=500)


class SecurityException(OmniSightException):
    """Raised when a request violates a security policy (e.g. SSRF, invalid URL scheme)."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=400)
