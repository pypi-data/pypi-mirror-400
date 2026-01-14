"""
Chat with human capability (v3 - workspace edition).

Implements the proactive communication behavior from v2/mai-tai-mode.md sections 3 and 6.

The existing `ask_human` MCP tool is treated as a general "chat_with_human" capability:
- Use for plan confirmation, priority clarification, and significant tradeoffs
- Prefer non-blocking or short-wait usage for status updates
- Keep messages brief, clear, and friendly
"""

import logging
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Priority level for messages to the human."""

    # Status updates, completion summaries - don't wait for response
    STATUS = "status"

    # Questions that would be nice to have answered but can proceed without
    LOW = "low"

    # Significant decisions that affect direction, UX, or scope
    MEDIUM = "medium"

    # Blocking issues that require human input to proceed
    HIGH = "high"


class DecisionCategory(Enum):
    """Categories of decisions for heuristic evaluation."""

    # Architecture choices (e.g., which pattern to use)
    ARCHITECTURE = "architecture"

    # User-facing changes (e.g., UI, API changes)
    USER_FACING = "user_facing"

    # Cost implications (e.g., choosing services, resources)
    COST = "cost"

    # Security-related decisions
    SECURITY = "security"

    # Scope changes (e.g., adding/removing features)
    SCOPE = "scope"

    # Implementation details (usually don't need human input)
    IMPLEMENTATION = "implementation"

    # Testing approach
    TESTING = "testing"


@dataclass
class DecisionContext:
    """Context for a decision that might need human input."""

    category: DecisionCategory
    description: str
    options: list[str]
    recommendation: Optional[str] = None
    reversible: bool = True
    affects_user: bool = False
    affects_cost: bool = False


def should_ask_human(context: DecisionContext) -> bool:
    """Determine if a decision should involve the human.

    Per mai-tai-mode.md section 3:
    - If a decision could change what the human sees, pays for, or depends on,
      lean toward chatting with the human
    - If it is a tiny internal detail, decide autonomously

    Args:
        context: The decision context

    Returns:
        True if the human should be consulted
    """
    # Always ask for security decisions
    if context.category == DecisionCategory.SECURITY:
        logger.info(f"Decision requires human input: security-related - {context.description}")
        return True

    # Always ask for cost implications
    if context.affects_cost or context.category == DecisionCategory.COST:
        logger.info(f"Decision requires human input: cost implications - {context.description}")
        return True

    # Always ask for user-facing changes
    if context.affects_user or context.category == DecisionCategory.USER_FACING:
        logger.info(f"Decision requires human input: user-facing - {context.description}")
        return True

    # Ask for scope changes
    if context.category == DecisionCategory.SCOPE:
        logger.info(f"Decision requires human input: scope change - {context.description}")
        return True

    # Ask for architecture decisions if not easily reversible
    if context.category == DecisionCategory.ARCHITECTURE and not context.reversible:
        logger.info(f"Decision requires human input: irreversible architecture - {context.description}")
        return True

    # Implementation details and testing can usually be decided autonomously
    if context.category in (DecisionCategory.IMPLEMENTATION, DecisionCategory.TESTING):
        logger.debug(f"Decision can be made autonomously: {context.category.value} - {context.description}")
        return False

    # Default: if there are multiple options and no clear recommendation, ask
    if len(context.options) > 1 and not context.recommendation:
        logger.info(f"Decision requires human input: multiple options, no recommendation - {context.description}")
        return True

    return False


def format_decision_request(context: DecisionContext) -> str:
    """Format a decision request message for the human.

    Args:
        context: The decision context

    Returns:
        Formatted message
    """
    lines = []

    lines.append("**Decision needed**")
    lines.append("")
    lines.append(context.description)
    lines.append("")
    lines.append("**Options:**")
    for i, option in enumerate(context.options, 1):
        lines.append(f"{i}. {option}")

    if context.recommendation:
        lines.append("")
        lines.append(f"**My recommendation:** {context.recommendation}")

    lines.append("")
    lines.append("Which would you prefer?")

    return "\n".join(lines)


def get_recommended_timeout(priority: MessagePriority) -> int:
    """Get recommended timeout in seconds based on message priority.

    Args:
        priority: The message priority

    Returns:
        Timeout in seconds
    """
    timeouts = {
        MessagePriority.STATUS: 0,      # Don't wait for status updates
        MessagePriority.LOW: 60,        # 1 minute for low priority
        MessagePriority.MEDIUM: 300,    # 5 minutes for medium
        MessagePriority.HIGH: 1800,     # 30 minutes for blocking issues
    }
    return timeouts.get(priority, 300)


async def chat_with_human(
    send_message: Callable[[str, str], Any],
    workspace_id: str,
    content: str,
    priority: MessagePriority = MessagePriority.STATUS,
    wait_for_response: bool = False,
) -> Optional[str]:
    """Send a message to the human via the mai-tai workspace.

    This is the primary "chat with human" capability per mai-tai-mode.md section 6.

    Args:
        send_message: Async function to send messages
        workspace_id: The mai-tai workspace ID
        content: Message content
        priority: Message priority (affects logging, not behavior)
        wait_for_response: Whether to wait for a response

    Returns:
        Response content if wait_for_response is True and response received, else None
    """
    logger.info(f"Chat with human [{priority.value}]: {content[:50]}...")
    await send_message(workspace_id, content)

    # Note: actual response waiting is handled by the caller using ask_human
    # This function is for non-blocking status updates
    return None


async def ask_for_decision(
    send_message: Callable[[str, str], Any],
    workspace_id: str,
    context: DecisionContext,
) -> None:
    """Ask the human for a decision.

    Args:
        send_message: Async function to send messages
        workspace_id: The mai-tai workspace ID
        context: The decision context
    """
    message = format_decision_request(context)
    await chat_with_human(
        send_message,
        workspace_id,
        message,
        priority=MessagePriority.MEDIUM,
    )
    logger.info(f"Asked human for decision: {context.description}")

