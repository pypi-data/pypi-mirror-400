import pytest
from unittest.mock import MagicMock
from soprano_sdk.nodes.collect_input import CollectInputStrategy, _get_agent_response
from soprano_sdk.core.constants import WorkflowKeys

class TestCollectInputStrategyRefactor:
    @pytest.fixture
    def strategy(self):
        step_config = {
            "field": "test_field",
            "agent": {"name": "test_agent"}
        }
        engine_context = MagicMock()
        engine_context.get_config_value.return_value = "history_based"
        return CollectInputStrategy(step_config, engine_context)

    def test_get_agent_response_success(self, strategy):
        agent = MagicMock()
        conversation = [{"role": "user", "content": "hello"}]

        mock_response = "response content"
        agent.invoke.return_value = mock_response

        response = _get_agent_response(agent, conversation)

        assert response == "response content"
        assert conversation[-1]["role"] == "assistant"
        assert conversation[-1]["content"] == "response content"

    def test_handle_max_attempts_default_message(self):
        """Test that default error message is used when on_max_attempts_reached is not provided"""
        step_config = {
            "id": "collect_customer_name",
            "field": "customer_name",
            "agent": {"name": "test_agent"}
        }
        engine_context = MagicMock()
        engine_context.get_config_value.return_value = "history_based"

        strategy = CollectInputStrategy(step_config, engine_context)
        state = {}

        result = strategy._handle_max_attempts(state)

        assert result[WorkflowKeys.STATUS] == "collect_customer_name_max_attempts"
        assert "customer_name" in result[WorkflowKeys.MESSAGES][0]
        assert "customer service" in result[WorkflowKeys.MESSAGES][0].lower()

    def test_handle_max_attempts_custom_message(self):
        """Test that custom error message is used when on_max_attempts_reached is provided"""
        custom_message = "Custom error: Too many attempts. Please call 1-800-SUPPORT."
        step_config = {
            "id": "collect_customer_name",
            "field": "customer_name",
            "agent": {"name": "test_agent"},
            "on_max_attempts_reached": custom_message
        }
        engine_context = MagicMock()
        engine_context.get_config_value.return_value = "history_based"

        strategy = CollectInputStrategy(step_config, engine_context)
        state = {}

        result = strategy._handle_max_attempts(state)

        assert result[WorkflowKeys.STATUS] == "collect_customer_name_max_attempts"
        assert result[WorkflowKeys.MESSAGES][0] == custom_message
        assert "1-800-SUPPORT" in result[WorkflowKeys.MESSAGES][0]
