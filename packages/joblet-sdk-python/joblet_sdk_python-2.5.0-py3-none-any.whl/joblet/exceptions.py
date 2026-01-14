"""Joblet SDK exceptions."""


class JobletException(Exception):
    """Base exception for all Joblet SDK errors."""

    pass


class JobletConnectionError(JobletException):
    """Can't connect to server."""

    pass


# Backward compatibility alias (deprecated)
ConnectionError = JobletConnectionError


class AuthenticationError(JobletException):
    """Authentication failed."""

    pass


class JobNotFoundError(JobletException):
    """Job not found."""

    pass


class JobOperationError(JobletException):
    """Job operation failed (run, stop, delete, etc.)."""

    pass


class RuntimeNotFoundError(JobletException):
    """Runtime not found."""

    pass


class NetworkError(JobletException):
    """Network operation failed."""

    pass


class VolumeError(JobletException):
    """Volume operation failed."""

    pass


class ValidationError(JobletException):
    """Invalid input."""

    pass


class JobletTimeoutError(JobletException):
    """Operation timed out."""

    pass


# Backward compatibility alias (deprecated)
TimeoutError = JobletTimeoutError
