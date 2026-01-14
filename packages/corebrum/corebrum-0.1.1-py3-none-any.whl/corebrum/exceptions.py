"""
Corebrum exception classes.
"""


class CorebrumError(Exception):
    """Base exception for all Corebrum errors."""
    pass


class TaskSubmissionError(CorebrumError):
    """Raised when task submission fails."""
    pass


class TaskExecutionError(CorebrumError):
    """Raised when task execution fails."""
    pass


class TaskTimeoutError(CorebrumError):
    """Raised when task execution times out."""
    pass

