"""
Tests for v2/v3 completion semantics.

Per v2/mai-tai-mode.md section 4:
- Agent should NOT exit when task is complete
- Mai-tai mode should remain True
- Agent should transition to idle state
- Agent should be ready for new instructions

Updated for v3 workspace edition (channel_id -> workspace_id).
"""

import pytest
from unittest.mock import AsyncMock

from mai_tai_mcp import (
    MaiTaiState,
    WorkPlan,
    PlanStep,
    EntryScenario,
    ActivityStatus,
    handle_task_complete,
    send_progress_update,
)


class TestCompletionSemantics:
    """Test that completion behavior keeps process alive."""

    def test_mai_tai_mode_remains_true_after_completion(self):
        """After task completion, mai_tai_mode should still be True."""
        state = MaiTaiState()
        plan = WorkPlan(
            task_summary="Test task",
            steps=[PlanStep("Step 1", completed=True)],
        )
        state.enter_mai_tai_mode(
            scenario=EntryScenario.WITH_PLAN,
            workspace_id="test-workspace",
            plan=plan,
        )

        # Simulate task completion by transitioning to idle
        state.transition_to_idle()

        # Key assertion: mai_tai_mode should remain True
        assert state.mai_tai_mode is True
        assert state.activity == ActivityStatus.IDLE

    def test_state_is_idle_after_completion(self):
        """After completion, activity should be IDLE not WORKING."""
        state = MaiTaiState()
        plan = WorkPlan(
            task_summary="Test task",
            steps=[PlanStep("Step 1")],
        )
        state.enter_mai_tai_mode(
            scenario=EntryScenario.WITH_PLAN,
            workspace_id="test-workspace",
            plan=plan,
        )

        assert state.activity == ActivityStatus.WORKING

        # Complete the step
        state.complete_current_step()

        # Should now be idle
        assert state.activity == ActivityStatus.IDLE

    def test_plan_cleared_after_completion(self):
        """After transition_to_idle, plan should be None."""
        state = MaiTaiState()
        plan = WorkPlan(
            task_summary="Test task",
            steps=[PlanStep("Step 1", completed=True)],
        )
        state.enter_mai_tai_mode(
            scenario=EntryScenario.WITH_PLAN,
            workspace_id="test-workspace",
            plan=plan,
        )

        state.transition_to_idle()

        assert state.plan is None

    def test_workspace_preserved_after_completion(self):
        """Workspace ID should be preserved for receiving new instructions."""
        state = MaiTaiState()
        plan = WorkPlan(
            task_summary="Test task",
            steps=[PlanStep("Step 1", completed=True)],
        )
        state.enter_mai_tai_mode(
            scenario=EntryScenario.WITH_PLAN,
            workspace_id="test-workspace",
            plan=plan,
        )

        state.transition_to_idle()

        # Workspace should still be set for receiving new instructions
        assert state.workspace_id == "test-workspace"

    @pytest.mark.asyncio
    async def test_handle_task_complete_sends_summary(self):
        """handle_task_complete should send a completion summary."""
        state = MaiTaiState()
        plan = WorkPlan(
            task_summary="Implement feature X",
            steps=[
                PlanStep("Step 1", completed=True),
                PlanStep("Step 2", completed=True),
            ],
        )
        state.enter_mai_tai_mode(
            scenario=EntryScenario.WITH_PLAN,
            workspace_id="test-workspace",
            plan=plan,
        )

        send_message = AsyncMock()

        await handle_task_complete(state, send_message)

        # Should have sent a message
        send_message.assert_called_once()
        workspace_id, content = send_message.call_args[0]
        assert workspace_id == "test-workspace"
        assert "Task completed" in content
        assert "Implement feature X" in content

    @pytest.mark.asyncio
    async def test_handle_task_complete_transitions_to_idle(self):
        """handle_task_complete should transition state to idle."""
        state = MaiTaiState()
        plan = WorkPlan(
            task_summary="Test task",
            steps=[PlanStep("Step 1", completed=True)],
        )
        state.enter_mai_tai_mode(
            scenario=EntryScenario.WITH_PLAN,
            workspace_id="test-workspace",
            plan=plan,
        )

        send_message = AsyncMock()

        await handle_task_complete(state, send_message)

        # Should be idle but still in mai-tai mode
        assert state.mai_tai_mode is True
        assert state.activity == ActivityStatus.IDLE

    @pytest.mark.asyncio
    async def test_progress_update_while_working(self):
        """Progress updates should work during mai-tai mode."""
        state = MaiTaiState()
        plan = WorkPlan(
            task_summary="Test task",
            steps=[PlanStep("Step 1"), PlanStep("Step 2")],
        )
        state.enter_mai_tai_mode(
            scenario=EntryScenario.WITH_PLAN,
            workspace_id="test-workspace",
            plan=plan,
        )

        send_message = AsyncMock()

        await send_progress_update(
            state, send_message,
            completed_step="Added login endpoint",
            next_step="Add JWT token generation",
        )

        send_message.assert_called_once()
        _, content = send_message.call_args[0]
        assert "Added login endpoint" in content
        assert "JWT token" in content

