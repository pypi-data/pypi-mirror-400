"""
Mai-Tai mode entry and exit handlers (v3 - workspace edition).

Implements the entry/exit semantics from v2/mai-tai-mode.md sections 2 and 5.
"""

import logging
from typing import Optional, Callable, Any

from .state import (
    MaiTaiState,
    EntryScenario,
    WorkPlan,
    PlanStep,
    ActivityStatus,
)

logger = logging.getLogger(__name__)


def format_initial_status_message(
    plan: WorkPlan,
    repo_name: Optional[str] = None,
) -> str:
    """Format the initial mai-tai mode status message.

    Per mai-tai-mode.md section 2.1, this should include:
    - Brief repo/project identification
    - Task in 1-2 sentences
    - Short numbered list of planned steps

    Args:
        plan: The work plan to summarize
        repo_name: Optional repository or project name

    Returns:
        Formatted status message
    """
    lines = []

    # Header with repo if available
    if repo_name or plan.repo_or_project:
        project = repo_name or plan.repo_or_project
        lines.append(f"**Mai-tai mode activated** for `{project}`")
    else:
        lines.append("**Mai-tai mode activated**")

    lines.append("")

    # Task summary
    lines.append(f"**Task:** {plan.task_summary}")
    lines.append("")

    # Planned steps
    if plan.steps:
        lines.append("**Plan:**")
        for i, step in enumerate(plan.steps, 1):
            status = "[x]" if step.completed else "[ ]"
            lines.append(f"{i}. {status} {step.description}")

    lines.append("")
    lines.append("I'll send updates as I make progress. Feel free to jump in anytime!")

    return "\n".join(lines)


def format_no_plan_request() -> str:
    """Format the message asking for a task (Scenario B).

    Per mai-tai-mode.md section 2.2.
    """
    return (
        "**Mai-tai mode activated** - but I need a task first!\n\n"
        "What would you like me to work on while you're away? "
        "Please be specific about:\n"
        "- What you want accomplished\n"
        "- Which files or areas to focus on\n"
        "- Any constraints or things to avoid\n\n"
        "Once you give me direction, I'll create a plan and get started."
    )


def format_exit_acknowledgment() -> str:
    """Format the mai-tai mode exit acknowledgment."""
    return (
        "**Mai-tai mode ended** - I'm back to normal operation.\n\n"
        "Let me know if you need anything else!"
    )


def format_completion_summary(
    plan: WorkPlan,
    follow_ups: Optional[list[str]] = None,
    caveats: Optional[list[str]] = None,
) -> str:
    """Format the completion summary message.

    Per mai-tai-mode.md section 4, this should include:
    - What was completed
    - Follow-up ideas (if any)
    - Caveats or limitations

    Args:
        plan: The completed work plan
        follow_ups: Optional list of follow-up suggestions
        caveats: Optional list of caveats or limitations
    """
    lines = []

    lines.append("**Task completed!**")
    lines.append("")
    lines.append(f"Finished: {plan.task_summary}")
    lines.append("")

    # Completed steps
    lines.append("**What was done:**")
    for i, step in enumerate(plan.steps, 1):
        if step.completed:
            lines.append(f"- {step.description}")

    # Follow-ups
    if follow_ups:
        lines.append("")
        lines.append("**Possible follow-ups:**")
        for item in follow_ups:
            lines.append(f"- {item}")

    # Caveats
    if caveats:
        lines.append("")
        lines.append("**Notes:**")
        for item in caveats:
            lines.append(f"- {item}")

    lines.append("")
    lines.append("I'm still here if you need anything else!")

    return "\n".join(lines)


def format_progress_update(
    completed_step: str,
    next_step: Optional[str] = None,
    notes: Optional[str] = None,
) -> str:
    """Format a progress update message.

    Per mai-tai-mode.md section 3.1, updates should be sent:
    - After completing a meaningful milestone
    - When starting a new major sub-task
    - When encountering persistent issues

    Args:
        completed_step: What was just completed
        next_step: What's coming next (optional)
        notes: Any additional notes or questions
    """
    lines = []

    lines.append(f"**Progress update**")
    lines.append("")
    lines.append(f"Completed: {completed_step}")

    if next_step:
        lines.append(f"Next: {next_step}")

    if notes:
        lines.append("")
        lines.append(notes)

    return "\n".join(lines)


def format_blocked_message(
    issue: str,
    tried: Optional[list[str]] = None,
    question: Optional[str] = None,
) -> str:
    """Format a message when blocked and needing human input.

    Args:
        issue: What's blocking progress
        tried: What was already attempted
        question: Specific question for the human
    """
    lines = []

    lines.append("**Need your input**")
    lines.append("")
    lines.append(f"I'm stuck on: {issue}")

    if tried:
        lines.append("")
        lines.append("What I tried:")
        for item in tried:
            lines.append(f"- {item}")

    if question:
        lines.append("")
        lines.append(f"**Question:** {question}")

    return "\n".join(lines)


async def send_progress_update(
    state: MaiTaiState,
    send_message: Callable[[str, str], Any],
    completed_step: str,
    next_step: Optional[str] = None,
    notes: Optional[str] = None,
) -> None:
    """Send a progress update to the mai-tai workspace.

    Args:
        state: The MaiTaiState
        send_message: Async function to send messages
        completed_step: What was just completed
        next_step: What's coming next
        notes: Any additional notes
    """
    if not state.mai_tai_mode or not state.workspace_id:
        logger.warning("send_progress_update called but not in mai-tai mode")
        return

    message = format_progress_update(completed_step, next_step, notes)
    await send_message(state.workspace_id, message)
    logger.info(f"Sent progress update: {completed_step}")


async def send_blocked_message(
    state: MaiTaiState,
    send_message: Callable[[str, str], Any],
    issue: str,
    tried: Optional[list[str]] = None,
    question: Optional[str] = None,
) -> None:
    """Send a blocked/need-input message to the mai-tai workspace.

    Args:
        state: The MaiTaiState
        send_message: Async function to send messages
        issue: What's blocking progress
        tried: What was already attempted
        question: Specific question for the human
    """
    if not state.mai_tai_mode or not state.workspace_id:
        logger.warning("send_blocked_message called but not in mai-tai mode")
        return

    state.activity = ActivityStatus.BLOCKED
    message = format_blocked_message(issue, tried, question)
    await send_message(state.workspace_id, message)
    logger.info(f"Sent blocked message: {issue}")


async def handle_enter_mai_tai_mode(
    state: MaiTaiState,
    workspace_id: str,
    send_message: Callable[[str, str], Any],
    plan: Optional[WorkPlan] = None,
    repo_name: Optional[str] = None,
) -> None:
    """Handle entering mai-tai mode.

    Args:
        state: The MaiTaiState to update
        workspace_id: Workspace for communications
        send_message: Async function to send messages (workspace_id, content)
        plan: Optional existing work plan (Scenario A)
        repo_name: Optional repository name
    """
    if plan:
        # Scenario A: Plan exists
        state.enter_mai_tai_mode(
            scenario=EntryScenario.WITH_PLAN,
            workspace_id=workspace_id,
            plan=plan,
        )
        message = format_initial_status_message(plan, repo_name)
    else:
        # Scenario B: No plan yet
        state.enter_mai_tai_mode(
            scenario=EntryScenario.NO_PLAN,
            workspace_id=workspace_id,
        )
        message = format_no_plan_request()

    await send_message(workspace_id, message)
    state.initial_status_sent = True
    logger.info(f"Sent initial mai-tai mode message to workspace {workspace_id}")


async def handle_exit_mai_tai_mode(
    state: MaiTaiState,
    send_message: Callable[[str, str], Any],
) -> None:
    """Handle exiting mai-tai mode.

    Args:
        state: The MaiTaiState to update
        send_message: Async function to send messages (workspace_id, content)
    """
    if not state.mai_tai_mode:
        logger.warning("handle_exit_mai_tai_mode called but not in mai-tai mode")
        return

    workspace_id = state.workspace_id
    state.exit_mai_tai_mode()

    if workspace_id:
        message = format_exit_acknowledgment()
        await send_message(workspace_id, message)
        logger.info(f"Sent exit acknowledgment to workspace {workspace_id}")


async def handle_plan_received(
    state: MaiTaiState,
    plan: WorkPlan,
    send_message: Callable[[str, str], Any],
    repo_name: Optional[str] = None,
) -> None:
    """Handle receiving a plan in Scenario B (no plan at entry).

    Args:
        state: The MaiTaiState to update
        plan: The work plan received from the human
        send_message: Async function to send messages
        repo_name: Optional repository name
    """
    if not state.mai_tai_mode:
        logger.warning("handle_plan_received called but not in mai-tai mode")
        return

    if state.entry_scenario != EntryScenario.NO_PLAN:
        logger.warning("handle_plan_received called but not in NO_PLAN scenario")
        return

    state.set_plan(plan)

    if state.workspace_id:
        message = format_initial_status_message(plan, repo_name)
        await send_message(state.workspace_id, message)
        logger.info(f"Sent plan confirmation to workspace {state.workspace_id}")


async def handle_task_complete(
    state: MaiTaiState,
    send_message: Callable[[str, str], Any],
    follow_ups: Optional[list[str]] = None,
    caveats: Optional[list[str]] = None,
) -> None:
    """Handle task completion (stay alive, don't exit).

    Per mai-tai-mode.md section 4:
    - Send completion summary
    - Transition to idle but keep mai_tai_mode True
    - Do NOT exit the process

    Args:
        state: The MaiTaiState to update
        send_message: Async function to send messages
        follow_ups: Optional follow-up suggestions
        caveats: Optional caveats or limitations
    """
    if not state.mai_tai_mode:
        logger.warning("handle_task_complete called but not in mai-tai mode")
        return

    if not state.plan:
        logger.warning("handle_task_complete called but no plan exists")
        return

    # Send completion summary
    if state.workspace_id:
        message = format_completion_summary(state.plan, follow_ups, caveats)
        await send_message(state.workspace_id, message)
        logger.info(f"Sent completion summary to workspace {state.workspace_id}")

    # Transition to idle - but stay in mai-tai mode!
    state.transition_to_idle()


def is_exit_request(message: str) -> bool:
    """Check if a message is a request to exit mai-tai mode.

    Args:
        message: The message content to check

    Returns:
        True if the message indicates exit intent
    """
    message_lower = message.lower().strip()

    exit_phrases = [
        "exit mai-tai mode",
        "exit mai-tai",
        "leave mai-tai mode",
        "leave mai-tai",
        "stop mai-tai mode",
        "stop mai-tai",
        "end mai-tai mode",
        "end mai-tai",
        "i'm back",
        "im back",
        "i am back",
        "you can stop",
        "you can stop now",
        "exit autonomous mode",
        "stop autonomous mode",
    ]

    return any(phrase in message_lower for phrase in exit_phrases)

