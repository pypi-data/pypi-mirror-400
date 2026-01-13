"""Type stubs for hfortix_fortios package."""

from __future__ import annotations

from hfortix_core import (
    APIError as APIError,
    AuthenticationError as AuthenticationError,
    AuthorizationError as AuthorizationError,
    BadRequestError as BadRequestError,
    CircuitBreakerOpenError as CircuitBreakerOpenError,
    ConfigurationError as ConfigurationError,
    DebugSession as DebugSession,
    DuplicateEntryError as DuplicateEntryError,
    EntryInUseError as EntryInUseError,
    FortinetError as FortinetError,
    InvalidValueError as InvalidValueError,
    MethodNotAllowedError as MethodNotAllowedError,
    NonRetryableError as NonRetryableError,
    OperationNotSupportedError as OperationNotSupportedError,
    PermissionDeniedError as PermissionDeniedError,
    RateLimitError as RateLimitError,
    ReadOnlyModeError as ReadOnlyModeError,
    ResourceNotFoundError as ResourceNotFoundError,
    RetryableError as RetryableError,
    ServerError as ServerError,
    ServiceUnavailableError as ServiceUnavailableError,
    TimeoutError as TimeoutError,
    VDOMError as VDOMError,
    debug_timer as debug_timer,
    format_connection_stats as format_connection_stats,
    format_request_info as format_request_info,
    print_debug_info as print_debug_info,
)
from hfortix_fortios.client import FortiOS as FortiOS
from hfortix_fortios.models import FortiObject as FortiObject

__version__: str

__all__ = [
    "FortiOS",
    "FortiObject",
    "configure_logging",
    "DebugSession",
    "debug_timer",
    "format_connection_stats",
    "format_request_info",
    "print_debug_info",
    "FortinetError",
    "APIError",
    "AuthenticationError",
    "AuthorizationError",
    "RetryableError",
    "NonRetryableError",
    "ConfigurationError",
    "VDOMError",
    "OperationNotSupportedError",
    "ReadOnlyModeError",
    "ResourceNotFoundError",
    "PermissionDeniedError",
    "MethodNotAllowedError",
    "BadRequestError",
    "DuplicateEntryError",
    "EntryInUseError",
    "InvalidValueError",
    "RateLimitError",
    "CircuitBreakerOpenError",
    "ServerError",
    "ServiceUnavailableError",
    "TimeoutError",
]

def configure_logging(
    level: str = "INFO",
    format: str | None = None,
    datefmt: str | None = None,
) -> None:
    """
    Configure logging for hfortix_fortios package.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format: Log message format string
        datefmt: Date format string
    """
    ...
