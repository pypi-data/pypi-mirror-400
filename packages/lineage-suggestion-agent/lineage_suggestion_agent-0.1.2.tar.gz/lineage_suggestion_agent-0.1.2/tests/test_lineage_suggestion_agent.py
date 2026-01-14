import pytest
from unittest.mock import patch, MagicMock, ANY
from lineage_suggestion_agent.agent import LineageSuggestionAgent
from lineage_suggestion_agent.config import LineageConfig
from lineage_suggestion_agent.models import LineageSuggestion

@pytest.fixture
def agent():
    """Fixture to create a LineageSuggestionAgent with a mock config."""
    with patch('lineage_suggestion_agent.agent.SFNAIHandler') as mock_ai_handler:
        config = LineageConfig(
            lineage_ai_provider="mock_provider",
            lineage_model="mock_model",
        )
        agent = LineageSuggestionAgent(config=config)
        # Attach the mock to the agent instance for easy access in tests
        agent.ai_handler = mock_ai_handler.return_value
        yield agent

def test_execute_task_success(agent):
    """Test the execute_task method for a successful LLM call."""
    # Arrange
    task = {"context": "Test context"}
    expected_suggestion = LineageSuggestion(answer="Test suggestion")
    expected_cost = {"total_cost_usd": 0.001}

    # Mock the return value of the ai_handler's route_to method
    agent.ai_handler.route_to.return_value = (expected_suggestion, expected_cost)

    # Act
    response, cost = agent.execute_task(task)

    # Assert
    assert response == expected_suggestion
    assert cost == expected_cost

    # Verify that the llm_call was made with the correct parameters
    agent.ai_handler.route_to.assert_called_once()
    call_args, call_kwargs = agent.ai_handler.route_to.call_args
    
    assert call_kwargs['llm_provider'] == "mock_provider"
    assert call_kwargs['model'] == "mock_model"
    
    messages = call_kwargs['configuration']['messages']
    assert any(msg['role'] == 'user' and 'Test context' in msg['content'] for msg in messages)

def test_call_method(agent):
    """Test that the __call__ method is an alias for execute_task."""
    task = {"context": "Another test context"}
    expected_suggestion = LineageSuggestion(answer="Another suggestion")
    expected_cost = {"total_cost_usd": 0.002}

    agent.ai_handler.route_to.return_value = (expected_suggestion, expected_cost)

    response, cost = agent(task)

    assert response == expected_suggestion
    assert cost == expected_cost
    agent.ai_handler.route_to.assert_called_once_with(
        llm_provider='mock_provider',
        model='mock_model',
        configuration=ANY
    )
