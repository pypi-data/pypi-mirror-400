"""
Observability utilities for Mai-Tai MCP (v2).

Provides structured logging and metrics for:
- Connection state changes
- Retry attempts and backoff
- Mai-tai mode events
- Message volume
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of observable events."""

    # Connection events
    CONNECTION_ATTEMPT = "connection_attempt"
    CONNECTION_SUCCESS = "connection_success"
    CONNECTION_FAILED = "connection_failed"
    CONNECTION_LOST = "connection_lost"
    RECONNECT_ATTEMPT = "reconnect_attempt"

    # Mai-tai mode events
    MAI_TAI_ENTER = "mai_tai_enter"
    MAI_TAI_EXIT = "mai_tai_exit"
    MAI_TAI_TASK_START = "mai_tai_task_start"
    MAI_TAI_TASK_COMPLETE = "mai_tai_task_complete"
    MAI_TAI_BLOCKED = "mai_tai_blocked"

    # Message events
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"

    # Error events
    ERROR_RECOVERABLE = "error_recoverable"
    ERROR_FATAL = "error_fatal"


@dataclass
class Metrics:
    """Runtime metrics for observability."""

    # Connection metrics
    connection_attempts: int = 0
    connection_successes: int = 0
    connection_failures: int = 0
    reconnect_attempts: int = 0

    # Message metrics
    messages_sent: int = 0
    messages_received: int = 0

    # Error metrics
    recoverable_errors: int = 0
    fatal_errors: int = 0

    # Timing
    start_time: float = field(default_factory=time.time)
    last_connection_time: Optional[float] = None
    total_connected_seconds: float = 0.0

    def uptime_seconds(self) -> float:
        """Get total uptime in seconds."""
        return time.time() - self.start_time

    def connection_success_rate(self) -> float:
        """Get connection success rate (0.0 to 1.0)."""
        total = self.connection_attempts
        if total == 0:
            return 0.0
        return self.connection_successes / total


# Global metrics instance
_metrics = Metrics()


def get_metrics() -> Metrics:
    """Get the global metrics instance."""
    return _metrics


def reset_metrics() -> None:
    """Reset all metrics (useful for testing)."""
    global _metrics
    _metrics = Metrics()


def log_event(
    event_type: EventType,
    message: str,
    **extra: any,
) -> None:
    """Log a structured event.

    Args:
        event_type: The type of event
        message: Human-readable message
        **extra: Additional structured data
    """
    # Update metrics based on event type
    metrics = get_metrics()

    if event_type == EventType.CONNECTION_ATTEMPT:
        metrics.connection_attempts += 1
    elif event_type == EventType.CONNECTION_SUCCESS:
        metrics.connection_successes += 1
        metrics.last_connection_time = time.time()
    elif event_type == EventType.CONNECTION_FAILED:
        metrics.connection_failures += 1
    elif event_type == EventType.RECONNECT_ATTEMPT:
        metrics.reconnect_attempts += 1
    elif event_type == EventType.MESSAGE_SENT:
        metrics.messages_sent += 1
    elif event_type == EventType.MESSAGE_RECEIVED:
        metrics.messages_received += 1
    elif event_type == EventType.ERROR_RECOVERABLE:
        metrics.recoverable_errors += 1
    elif event_type == EventType.ERROR_FATAL:
        metrics.fatal_errors += 1

    # Determine log level
    if event_type in (EventType.ERROR_FATAL,):
        level = logging.ERROR
    elif event_type in (EventType.ERROR_RECOVERABLE, EventType.CONNECTION_FAILED):
        level = logging.WARNING
    elif event_type in (EventType.MAI_TAI_ENTER, EventType.MAI_TAI_EXIT,
                        EventType.CONNECTION_SUCCESS, EventType.MAI_TAI_TASK_COMPLETE):
        level = logging.INFO
    else:
        level = logging.DEBUG

    # Build structured log message
    extra_str = " ".join(f"{k}={v}" for k, v in extra.items()) if extra else ""
    log_message = f"[{event_type.value}] {message}"
    if extra_str:
        log_message += f" | {extra_str}"

    logger.log(level, log_message)


def log_connection_attempt(url: str) -> None:
    """Log a connection attempt."""
    log_event(EventType.CONNECTION_ATTEMPT, f"Connecting to {url}", url=url)


def log_connection_success(url: str) -> None:
    """Log a successful connection."""
    log_event(EventType.CONNECTION_SUCCESS, f"Connected to {url}", url=url)


def log_connection_failed(url: str, error: str) -> None:
    """Log a failed connection."""
    log_event(EventType.CONNECTION_FAILED, f"Connection failed: {error}", url=url, error=error)


def log_connection_lost(reason: str) -> None:
    """Log a lost connection."""
    log_event(EventType.CONNECTION_LOST, f"Connection lost: {reason}", reason=reason)


def log_reconnect_attempt(attempt: int, delay: float) -> None:
    """Log a reconnection attempt."""
    log_event(
        EventType.RECONNECT_ATTEMPT,
        f"Reconnecting (attempt {attempt}, delay {delay:.1f}s)",
        attempt=attempt,
        delay_seconds=delay,
    )


def log_mai_tai_enter(workspace_id: str, scenario: str) -> None:
    """Log entering mai-tai mode."""
    log_event(
        EventType.MAI_TAI_ENTER,
        f"Entered mai-tai mode ({scenario})",
        workspace_id=workspace_id,
        scenario=scenario,
    )


def log_mai_tai_exit(workspace_id: str) -> None:
    """Log exiting mai-tai mode."""
    log_event(EventType.MAI_TAI_EXIT, "Exited mai-tai mode", workspace_id=workspace_id)


def log_mai_tai_task_complete(task_summary: str) -> None:
    """Log task completion in mai-tai mode."""
    log_event(
        EventType.MAI_TAI_TASK_COMPLETE,
        f"Task completed: {task_summary}",
        task_summary=task_summary,
    )


def log_message_sent(workspace_id: str, content_preview: str) -> None:
    """Log a sent message."""
    preview = content_preview[:50] + "..." if len(content_preview) > 50 else content_preview
    log_event(EventType.MESSAGE_SENT, f"Sent: {preview}", workspace_id=workspace_id)


def log_message_received(workspace_id: str, content_preview: str) -> None:
    """Log a received message."""
    preview = content_preview[:50] + "..." if len(content_preview) > 50 else content_preview
    log_event(EventType.MESSAGE_RECEIVED, f"Received: {preview}", workspace_id=workspace_id)


def log_recoverable_error(error: str, will_retry: bool = True) -> None:
    """Log a recoverable error."""
    log_event(
        EventType.ERROR_RECOVERABLE,
        f"Recoverable error: {error}",
        error=error,
        will_retry=will_retry,
    )


def log_fatal_error(error: str) -> None:
    """Log a fatal error."""
    log_event(EventType.ERROR_FATAL, f"Fatal error: {error}", error=error)


def get_status_summary() -> dict:
    """Get a summary of current status for debugging.

    Returns:
        Dictionary with status information
    """
    metrics = get_metrics()
    return {
        "uptime_seconds": round(metrics.uptime_seconds(), 1),
        "connection_attempts": metrics.connection_attempts,
        "connection_success_rate": round(metrics.connection_success_rate(), 2),
        "reconnect_attempts": metrics.reconnect_attempts,
        "messages_sent": metrics.messages_sent,
        "messages_received": metrics.messages_received,
        "recoverable_errors": metrics.recoverable_errors,
        "fatal_errors": metrics.fatal_errors,
    }

