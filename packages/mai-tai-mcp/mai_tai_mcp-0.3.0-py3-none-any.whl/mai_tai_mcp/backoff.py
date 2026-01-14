"""Exponential backoff utility for mai-tai MCP server (v2).

Implements the retry policy from v2/runtime-loop.md section 4:
- Initial delay: ~2 seconds
- Backoff factor: 2x per consecutive failure
- Maximum delay: ~60 seconds
- Optional jitter: +/-20% random variation
- Reset on success
"""

import random
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BackoffState:
    """Tracks backoff state for retry logic.

    The runtime loop maintains one instance of this and passes it to
    backoff functions. On successful operations, call reset() to clear
    the failure count.
    """

    # Configuration
    initial_delay: float = 2.0  # seconds
    max_delay: float = 60.0  # seconds
    multiplier: float = 2.0  # exponential factor
    jitter: float = 0.2  # +/- 20% randomization

    # State
    consecutive_failures: int = field(default=0, repr=False)
    last_error_time: Optional[float] = field(default=None, repr=False)

    def reset(self) -> None:
        """Reset backoff state after a successful operation."""
        self.consecutive_failures = 0
        self.last_error_time = None

    def record_failure(self) -> None:
        """Record a failure and update the last error time."""
        self.consecutive_failures += 1
        self.last_error_time = time.time()

    def get_delay(self) -> float:
        """Calculate the next backoff delay.

        Returns the delay in seconds, incorporating exponential growth
        and optional jitter.
        """
        if self.consecutive_failures == 0:
            return 0.0

        # Exponential backoff: initial * (multiplier ^ (failures - 1))
        delay = self.initial_delay * (self.multiplier ** (self.consecutive_failures - 1))

        # Cap at maximum
        delay = min(delay, self.max_delay)

        # Apply jitter (+/- jitter percent)
        if self.jitter > 0:
            jitter_range = delay * self.jitter
            delay += random.uniform(-jitter_range, jitter_range)

        return max(0.0, delay)


def wait_with_backoff(state: BackoffState) -> float:
    """Wait for the appropriate backoff delay.

    Args:
        state: BackoffState tracking consecutive failures

    Returns:
        The number of seconds waited
    """
    delay = state.get_delay()
    if delay > 0:
        time.sleep(delay)
    return delay


def should_retry(state: BackoffState, max_retries: Optional[int] = None) -> bool:
    """Check if we should retry based on the current state.

    In v2, the runtime loop retries indefinitely for recoverable errors,
    so max_retries is optional and typically not used for the main loop.
    It's provided for cases where you want bounded retries (e.g., during
    initial connection).

    Args:
        state: BackoffState tracking consecutive failures
        max_retries: Optional maximum retry count. If None, always returns True.

    Returns:
        True if we should retry, False if we've exceeded max_retries
    """
    if max_retries is None:
        return True
    return state.consecutive_failures < max_retries


# =============================================================================
# Convenience context manager for backoff-wrapped operations
# =============================================================================


class BackoffRetry:
    """Context manager for operations that should retry with backoff.

    Example:
        state = BackoffState()
        while should_retry(state):
            try:
                result = do_operation()
                state.reset()
                break
            except RecoverableError:
                state.record_failure()
                wait_with_backoff(state)
    """

    def __init__(self, state: BackoffState):
        self.state = state
        self.succeeded = False

    def __enter__(self) -> "BackoffRetry":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is None:
            # Operation succeeded
            self.state.reset()
            self.succeeded = True
        else:
            # Operation failed - record failure but don't suppress exception
            self.state.record_failure()
        return False  # Don't suppress exceptions

