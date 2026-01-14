"""
Mai-Tai mode state management (v3 - workspace edition).

Tracks the agent's operational state including mai-tai mode, current plan,
and activity status per v2/mai-tai-mode.md.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ActivityStatus(Enum):
    """Agent's current activity status."""
    IDLE = "idle"           # No active work, waiting for instructions
    WORKING = "working"     # Actively executing a plan
    BLOCKED = "blocked"     # Waiting for human input to proceed


class EntryScenario(Enum):
    """How mai-tai mode was entered."""
    WITH_PLAN = "with_plan"     # Scenario A: plan already exists
    NO_PLAN = "no_plan"         # Scenario B: need to ask for task


@dataclass
class PlanStep:
    """A single step in the current plan."""
    description: str
    completed: bool = False


@dataclass
class WorkPlan:
    """The agent's current work plan."""
    task_summary: str
    steps: list[PlanStep] = field(default_factory=list)
    repo_or_project: Optional[str] = None

    def current_step_index(self) -> int:
        """Get the index of the first incomplete step, or -1 if all done."""
        for i, step in enumerate(self.steps):
            if not step.completed:
                return i
        return -1

    def is_complete(self) -> bool:
        """Check if all steps are complete."""
        return all(step.completed for step in self.steps)

    def mark_step_complete(self, index: int) -> None:
        """Mark a step as complete."""
        if 0 <= index < len(self.steps):
            self.steps[index].completed = True


@dataclass
class MaiTaiState:
    """Tracks the agent's mai-tai mode state.

    This is the central state object that tracks whether the agent is in
    mai-tai mode, what work plan it's executing, and its activity status.
    """
    # Core mai-tai mode flag
    mai_tai_mode: bool = False

    # How mai-tai mode was entered (if active)
    entry_scenario: Optional[EntryScenario] = None

    # Current activity status
    activity: ActivityStatus = ActivityStatus.IDLE

    # The active work plan (if any)
    plan: Optional[WorkPlan] = None

    # Workspace ID for mai-tai communications
    workspace_id: Optional[str] = None

    # Whether initial status message has been sent
    initial_status_sent: bool = False

    def enter_mai_tai_mode(
        self,
        scenario: EntryScenario,
        workspace_id: str,
        plan: Optional[WorkPlan] = None,
    ) -> None:
        """Enter mai-tai mode.

        Args:
            scenario: How mai-tai mode is being entered
            workspace_id: Workspace for mai-tai communications
            plan: Optional work plan (required for WITH_PLAN scenario)
        """
        if scenario == EntryScenario.WITH_PLAN and plan is None:
            raise ValueError("WITH_PLAN scenario requires a plan")

        self.mai_tai_mode = True
        self.entry_scenario = scenario
        self.workspace_id = workspace_id
        self.plan = plan
        self.initial_status_sent = False

        if plan:
            self.activity = ActivityStatus.WORKING
        else:
            self.activity = ActivityStatus.BLOCKED  # Waiting for plan

        logger.info(f"Entered mai-tai mode: scenario={scenario.value}, workspace={workspace_id}")

    def exit_mai_tai_mode(self) -> None:
        """Exit mai-tai mode but keep the process alive.
        
        The agent remains available for normal interactions.
        """
        if not self.mai_tai_mode:
            logger.warning("exit_mai_tai_mode called but not in mai-tai mode")
            return
        
        self.mai_tai_mode = False
        self.entry_scenario = None
        self.activity = ActivityStatus.IDLE
        self.plan = None
        self.initial_status_sent = False
        # Keep workspace_id for potential future communications

        logger.info("Exited mai-tai mode")

    def set_plan(self, plan: WorkPlan) -> None:
        """Set or update the work plan.
        
        Used in Scenario B after receiving task from human.
        """
        self.plan = plan
        if self.mai_tai_mode:
            self.activity = ActivityStatus.WORKING
        logger.info(f"Work plan set: {plan.task_summary}")

    def complete_current_step(self) -> bool:
        """Mark the current step as complete.
        
        Returns:
            True if there are more steps, False if plan is complete
        """
        if not self.plan:
            return False
        
        current = self.plan.current_step_index()
        if current >= 0:
            self.plan.mark_step_complete(current)
            logger.info(f"Completed step {current + 1}: {self.plan.steps[current].description}")
        
        if self.plan.is_complete():
            self.activity = ActivityStatus.IDLE
            return False
        return True

    def transition_to_idle(self) -> None:
        """Transition to idle state after completing work.
        
        Mai-tai mode remains active, waiting for new instructions.
        """
        self.activity = ActivityStatus.IDLE
        self.plan = None
        logger.info("Transitioned to idle (mai-tai mode still active)")

