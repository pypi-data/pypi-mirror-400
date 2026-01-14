"""Error types for mai-tai MCP server (v2).

This module defines the error hierarchy for the v2 runtime loop:

1. ConfigurationError - Startup errors that are always fatal
   - Missing or invalid environment variables
   - Invalid configuration values

2. RecoverableError - Runtime errors that should be retried
   - Network timeouts and connection errors
   - HTTP 5xx server errors
   - Temporary DNS failures
   - WebSocket disconnects (without explicit rejection)

3. FatalRuntimeError - Runtime errors that should terminate the agent
   - Authentication failures (401/403 after retries)
   - Protocol/version incompatibility
   - Unrecoverable internal errors

The runtime loop (server.py) uses these categories to decide whether to
retry with backoff or exit the process.
"""

from typing import Optional


class MaiTaiError(Exception):
    """Base exception for all Mai-Tai MCP errors."""

    pass


# =============================================================================
# Startup Errors (always fatal, no retry)
# =============================================================================


class ConfigurationError(MaiTaiError):
    """Raised when Mai-Tai MCP configuration is invalid or incomplete.

    These errors occur at startup before the main loop begins.
    The agent should exit immediately with a clear error message.
    """

    pass


# =============================================================================
# Runtime Errors
# =============================================================================


class RecoverableError(MaiTaiError):
    """Raised for transient errors that should be retried with backoff.

    Examples:
    - Network timeouts (ETIMEDOUT, ECONNRESET)
    - HTTP 5xx responses (server errors)
    - Temporary DNS failures
    - WebSocket disconnects without explicit rejection

    The runtime loop should catch these, apply backoff, and retry.
    """

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        retry_after: Optional[float] = None,
    ):
        super().__init__(message)
        self.original_error = original_error
        self.retry_after = retry_after  # Optional hint from server (e.g., Retry-After header)


class FatalRuntimeError(MaiTaiError):
    """Raised for unrecoverable runtime errors that should terminate the agent.

    Examples:
    - Authentication failures (401/403) that persist after retries
    - API key revoked or project deleted
    - Protocol/version incompatibility
    - Unrecoverable internal state corruption

    The runtime loop should:
    1. Log the error clearly
    2. Attempt to notify the human (best effort)
    3. Exit with non-zero status
    """

    def __init__(
        self,
        message: str,
        original_error: Optional[Exception] = None,
        should_notify_human: bool = True,
    ):
        super().__init__(message)
        self.original_error = original_error
        self.should_notify_human = should_notify_human


# =============================================================================
# HTTP Status Code Classification
# =============================================================================

# Status codes that indicate recoverable errors (retry with backoff)
RECOVERABLE_STATUS_CODES = {
    408,  # Request Timeout
    429,  # Too Many Requests
    500,  # Internal Server Error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
}

# Status codes that indicate fatal errors (stop retrying)
FATAL_STATUS_CODES = {
    401,  # Unauthorized (bad API key)
    403,  # Forbidden (key revoked, project access denied)
    404,  # Not Found (project deleted)
    410,  # Gone (resource permanently removed)
}


def classify_http_error(status_code: int, response_text: str = "") -> MaiTaiError:
    """Classify an HTTP error into recoverable or fatal.

    Args:
        status_code: HTTP status code
        response_text: Response body (for error message context)

    Returns:
        RecoverableError or FatalRuntimeError based on the status code
    """
    if status_code in RECOVERABLE_STATUS_CODES:
        return RecoverableError(
            f"HTTP {status_code}: {response_text[:200] if response_text else 'Server error'}"
        )

    if status_code in FATAL_STATUS_CODES:
        return FatalRuntimeError(
            f"HTTP {status_code}: {response_text[:200] if response_text else 'Access denied'}"
        )

    # Unknown 4xx errors are treated as fatal (client error, won't succeed on retry)
    if 400 <= status_code < 500:
        return FatalRuntimeError(f"HTTP {status_code}: {response_text[:200]}")

    # Unknown 5xx errors are treated as recoverable
    if status_code >= 500:
        return RecoverableError(f"HTTP {status_code}: {response_text[:200]}")

    # Shouldn't happen, but treat as recoverable to be safe
    return RecoverableError(f"Unexpected HTTP {status_code}")

