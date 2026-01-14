"""
Tests for AsyncFunctionStrategy - the call_async_function node type.
"""

import pytest
from unittest.mock import MagicMock, patch

from soprano_sdk.nodes.async_function import AsyncFunctionStrategy
from soprano_sdk.core.constants import WorkflowKeys


class TestAsyncFunctionStrategy:
    """Tests for AsyncFunctionStrategy."""

    @pytest.fixture
    def engine_context(self):
        """Create a mock engine context."""
        context = MagicMock()
        context.function_repository = MagicMock()
        context.outcome_map = {"success": {}, "failed": {}}
        return context

    @pytest.fixture
    def step_config(self):
        """Basic step config for async function."""
        return {
            "id": "async_validate",
            "action": "call_async_function",
            "function": "test_module.async_function",
            "output": "validation_result",
        }

    def test_init_requires_function(self, engine_context):
        """Test that function property is required."""
        step_config = {
            "id": "test_step",
            "output": "result",
        }
        with pytest.raises(RuntimeError, match="missing required 'function' property"):
            AsyncFunctionStrategy(step_config, engine_context)

    def test_init_requires_output(self, engine_context):
        """Test that output property is required."""
        step_config = {
            "id": "test_step",
            "function": "test.func",
        }
        with pytest.raises(RuntimeError, match="missing required 'output' property"):
            AsyncFunctionStrategy(step_config, engine_context)

    def test_init_success(self, step_config, engine_context):
        """Test successful initialization."""
        strategy = AsyncFunctionStrategy(step_config, engine_context)
        assert strategy.step_id == "async_validate"
        assert strategy.function_path == "test_module.async_function"
        assert strategy.output_field == "validation_result"

    def test_is_pending_result_true(self, step_config, engine_context):
        """Test detection of pending result."""
        strategy = AsyncFunctionStrategy(step_config, engine_context)

        pending_result = {"status": "pending", "job_id": "123"}
        assert strategy._is_pending_result(pending_result) is True

    def test_is_pending_result_false_different_status(self, step_config, engine_context):
        """Test non-pending status is not detected as pending."""
        strategy = AsyncFunctionStrategy(step_config, engine_context)

        completed_result = {"status": "completed", "value": True}
        assert strategy._is_pending_result(completed_result) is False

    def test_is_pending_result_false_not_dict(self, step_config, engine_context):
        """Test non-dict result is not detected as pending."""
        strategy = AsyncFunctionStrategy(step_config, engine_context)

        assert strategy._is_pending_result(True) is False
        assert strategy._is_pending_result("result") is False
        assert strategy._is_pending_result(123) is False

    def test_is_async_pending_true(self, step_config, engine_context):
        """Test detection of async pending state."""
        strategy = AsyncFunctionStrategy(step_config, engine_context)
        state = {WorkflowKeys.STATUS: "async_validate_pending"}

        assert strategy._is_async_pending(state) is True

    def test_is_async_pending_false(self, step_config, engine_context):
        """Test non-pending state is not detected as pending."""
        strategy = AsyncFunctionStrategy(step_config, engine_context)
        state = {WorkflowKeys.STATUS: "async_validate_success"}

        assert strategy._is_async_pending(state) is False

    def test_pending_key(self, step_config, engine_context):
        """Test pending key generation."""
        strategy = AsyncFunctionStrategy(step_config, engine_context)
        assert strategy._pending_key == "_async_pending_async_validate"

    def test_sync_completion_stores_result(self, step_config, engine_context):
        """Test that synchronous completion stores the result."""
        strategy = AsyncFunctionStrategy(step_config, engine_context)

        # Mock function that returns sync result (not pending)
        mock_func = MagicMock(return_value=True)
        engine_context.function_repository.load.return_value = mock_func

        state = {}

        with patch.object(strategy, '_handle_routing', return_value=state):
            strategy.execute(state)

        assert state["validation_result"] is True

    def test_sync_completion_tracks_computed_field(self, step_config, engine_context):
        """Test that synchronous completion tracks computed fields."""
        strategy = AsyncFunctionStrategy(step_config, engine_context)

        mock_func = MagicMock(return_value={"result": "success"})
        engine_context.function_repository.load.return_value = mock_func

        state = {}

        with patch.object(strategy, '_handle_routing', return_value=state):
            strategy.execute(state)

        assert "validation_result" in state.get(WorkflowKeys.COMPUTED_FIELDS, [])

    def test_transition_routing_matches_condition(self, engine_context):
        """Test transition routing with matching condition."""
        step_config = {
            "id": "async_validate",
            "function": "test.func",
            "output": "result",
            "transitions": [
                {"condition": True, "next": "next_step"},
                {"condition": False, "next": "failed"},
            ]
        }
        strategy = AsyncFunctionStrategy(step_config, engine_context)

        mock_func = MagicMock(return_value=True)
        engine_context.function_repository.load.return_value = mock_func

        state = {}
        result = strategy.execute(state)

        assert result[WorkflowKeys.STATUS] == "async_validate_next_step"

    def test_transition_routing_with_ref(self, engine_context):
        """Test transition routing with nested ref field."""
        step_config = {
            "id": "async_validate",
            "function": "test.func",
            "output": "result",
            "transitions": [
                {"condition": "approved", "next": "success", "ref": "status"},
                {"condition": "rejected", "next": "failed", "ref": "status"},
            ]
        }
        strategy = AsyncFunctionStrategy(step_config, engine_context)

        mock_func = MagicMock(return_value={"status": "approved", "score": 95})
        engine_context.function_repository.load.return_value = mock_func

        state = {}
        result = strategy.execute(state)

        assert result[WorkflowKeys.STATUS] == "async_validate_success"

    def test_transition_routing_list_condition(self, engine_context):
        """Test transition routing with list of conditions."""
        step_config = {
            "id": "async_validate",
            "function": "test.func",
            "output": "result",
            "transitions": [
                {"condition": ["approved", "verified"], "next": "success"},
                {"condition": ["rejected", "failed"], "next": "failed"},
            ]
        }
        strategy = AsyncFunctionStrategy(step_config, engine_context)

        mock_func = MagicMock(return_value="verified")
        engine_context.function_repository.load.return_value = mock_func

        state = {}
        result = strategy.execute(state)

        assert result[WorkflowKeys.STATUS] == "async_validate_success"

    def test_simple_routing_with_next_step(self, engine_context):
        """Test simple routing when no transitions defined."""
        step_config = {
            "id": "async_validate",
            "function": "test.func",
            "output": "result",
            "next": "process_result",
        }
        strategy = AsyncFunctionStrategy(step_config, engine_context)

        mock_func = MagicMock(return_value=True)
        engine_context.function_repository.load.return_value = mock_func

        state = {}
        result = strategy.execute(state)

        assert result[WorkflowKeys.STATUS] == "async_validate_process_result"

    def test_simple_routing_sets_outcome(self, engine_context):
        """Test that routing to outcome sets outcome_id."""
        step_config = {
            "id": "async_validate",
            "function": "test.func",
            "output": "result",
            "next": "success",
        }
        strategy = AsyncFunctionStrategy(step_config, engine_context)

        mock_func = MagicMock(return_value=True)
        engine_context.function_repository.load.return_value = mock_func

        state = {}
        result = strategy.execute(state)

        assert result[WorkflowKeys.OUTCOME_ID] == "success"

    def test_function_load_error(self, step_config, engine_context):
        """Test handling of function load error."""
        strategy = AsyncFunctionStrategy(step_config, engine_context)

        engine_context.function_repository.load.side_effect = ImportError("Module not found")

        state = {}
        with pytest.raises(RuntimeError, match="Failed to load function"):
            strategy.execute(state)

    def test_function_execution_error(self, step_config, engine_context):
        """Test handling of function execution error."""
        strategy = AsyncFunctionStrategy(step_config, engine_context)

        mock_func = MagicMock(side_effect=ValueError("Invalid input"))
        engine_context.function_repository.load.return_value = mock_func

        state = {}
        with pytest.raises(RuntimeError, match="Function.*failed"):
            strategy.execute(state)


class TestAsyncFunctionPendingBehavior:
    """Tests for async pending interrupt behavior."""

    @pytest.fixture
    def engine_context(self):
        context = MagicMock()
        context.function_repository = MagicMock()
        context.outcome_map = {}
        return context

    @pytest.fixture
    def step_config(self):
        return {
            "id": "async_validate",
            "function": "test.func",
            "output": "result",
            "transitions": [
                {"condition": True, "next": "success"},
                {"condition": False, "next": "failed"},
            ]
        }

    def test_pending_result_sets_status(self, step_config, engine_context):
        """Test that pending result sets status to pending."""
        strategy = AsyncFunctionStrategy(step_config, engine_context)

        mock_func = MagicMock(return_value={"status": "pending", "job_id": "abc123"})
        engine_context.function_repository.load.return_value = mock_func

        state = {}

        # Mock interrupt to simulate the async pause
        # interrupt() returns the resume value when called during resume
        with patch('soprano_sdk.nodes.async_function.interrupt', return_value=True) as mock_interrupt:
            strategy.execute(state)

            # Verify interrupt was called with correct async metadata
            mock_interrupt.assert_called_once()
            call_args = mock_interrupt.call_args[0][0]
            assert call_args["type"] == "async"
            assert call_args["step_id"] == "async_validate"
            assert call_args["pending"]["status"] == "pending"
            assert call_args["pending"]["job_id"] == "abc123"

    def test_pending_result_stores_metadata_before_interrupt(self, step_config, engine_context):
        """Test that pending result stores metadata in state before interrupt."""
        strategy = AsyncFunctionStrategy(step_config, engine_context)

        pending_metadata = {"status": "pending", "job_id": "abc123", "callback_url": "http://..."}
        mock_func = MagicMock(return_value=pending_metadata)
        engine_context.function_repository.load.return_value = mock_func

        state = {}
        stored_state = {}

        # Custom interrupt mock that captures state at the moment of interrupt
        def capture_state_interrupt(value):
            stored_state.update(dict(state))  # Copy state at interrupt time
            return True  # Return resume value

        with patch('soprano_sdk.nodes.async_function.interrupt', side_effect=capture_state_interrupt):
            strategy.execute(state)

        # Check that metadata was stored before interrupt
        assert stored_state["_async_pending_async_validate"] == pending_metadata
        assert stored_state[WorkflowKeys.STATUS] == "async_validate_pending"

    def test_resume_cleans_up_pending_metadata(self, step_config, engine_context):
        """Test that resuming cleans up pending metadata from state."""
        strategy = AsyncFunctionStrategy(step_config, engine_context)

        pending_metadata = {"status": "pending", "job_id": "abc123"}
        mock_func = MagicMock(return_value=pending_metadata)
        engine_context.function_repository.load.return_value = mock_func

        state = {}

        # Simulate the full flow: first call sets pending, second call (resume) cleans up
        with patch('soprano_sdk.nodes.async_function.interrupt', return_value=True):
            strategy.execute(state)

        # After resume (interrupt returns async result), pending key should be cleaned up
        assert "_async_pending_async_validate" not in state

    def test_resume_uses_async_result_for_routing(self, step_config, engine_context):
        """Test that async result from resume is used for routing."""
        strategy = AsyncFunctionStrategy(step_config, engine_context)

        pending_metadata = {"status": "pending", "job_id": "abc123"}
        mock_func = MagicMock(return_value=pending_metadata)
        engine_context.function_repository.load.return_value = mock_func

        state = {}

        # Mock interrupt to return True (simulating resume with async_result=True)
        with patch('soprano_sdk.nodes.async_function.interrupt', return_value=True):
            result = strategy.execute(state)

        # Result should be True (from the mocked interrupt return value)
        assert state["result"] is True
        assert result[WorkflowKeys.STATUS] == "async_validate_success"


class TestAsyncFunctionNodeFactory:
    """Test that AsyncFunctionStrategy is properly registered."""

    def test_factory_registration(self):
        """Test that call_async_function is registered in NodeFactory."""
        from soprano_sdk.nodes.factory import NodeFactory
        from soprano_sdk.core.constants import ActionType

        assert NodeFactory.is_registered(ActionType.CALL_ASYNC_FUNCTION.value)

    def test_factory_creates_async_strategy(self):
        """Test that factory creates AsyncFunctionStrategy for call_async_function."""
        from soprano_sdk.nodes.factory import NodeFactory

        step_config = {
            "id": "test_async",
            "action": "call_async_function",
            "function": "test.func",
            "output": "result",
        }
        engine_context = MagicMock()
        engine_context.function_repository = MagicMock()
        engine_context.outcome_map = {}

        node_fn = NodeFactory.create(step_config, engine_context)

        # The returned function should be callable
        assert callable(node_fn)
