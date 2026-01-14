
import json
import pytest
from unittest.mock import MagicMock, patch
from collections import namedtuple

from src.ml_approach_suggestion_agent.agent import MLApproachDecisionAgent
from src.ml_approach_suggestion_agent.models import MethodologyRecommendation

# Mock data for testing
domain_obj = namedtuple("Domain", ["domain_name", "domain_description"])
use_case_obj = namedtuple("UseCase", ["use_case_name", "use_case_description"])

mock_domain = domain_obj("E-commerce", "Online retail platform")
mock_use_case = use_case_obj("Customer Churn Prediction", "Predict which customers are likely to churn")
mock_column_descriptions = "user_id: string, purchase_history: array, last_login: date"
mock_column_insights = "High cardinality in user_id"


@pytest.fixture
def agent():
    """Fixture for MLApproachDecisionAgent."""
    with patch('src.ml_approach_suggestion_agent.agent.SFNAIHandler') as mock_ai_handler:
        agent = MLApproachDecisionAgent()
        agent.ai_handler = mock_ai_handler()
        yield agent

def test_suggest_approach_success(agent):
    """Test successful suggestion of an ML approach."""
    mock_response = {
        "selected_methodology": "binary_classification",
        "justification": "The use case is a classic classification problem."
    }
    cost_summary = {'prompt_tokens': 213, 'completion_tokens': 125, 'total_tokens': 338, 'total_cost_usd': 0.0018}
    agent.ai_handler.route_to.return_value = (MethodologyRecommendation(**mock_response), cost_summary)
    result, cost = agent.suggest_approach(mock_domain.domain_name, mock_domain.domain_description, mock_use_case, mock_column_descriptions, mock_column_insights)

    assert isinstance(result, MethodologyRecommendation)
    assert result.selected_methodology == "binary_classification"
    assert cost == cost_summary

def test_suggest_approach_failure_json(agent):
    """Test failure due to invalid JSON response."""
    agent.ai_handler.route_to.side_effect = Exception("Simulating JSON parsing error")
    result, cost = agent.suggest_approach(mock_domain.domain_name, mock_domain.domain_description, mock_use_case, mock_column_descriptions, mock_column_insights, max_try=1)

    assert result == {}
    assert cost == {}

def test_suggest_approach_api_error(agent):
    """Test failure due to an API error."""
    agent.ai_handler.route_to.side_effect = Exception("API Error")

    result, cost = agent.suggest_approach(mock_domain.domain_name, mock_domain.domain_description, mock_use_case, mock_column_descriptions, mock_column_insights, max_try=1)

    assert result == {}
    assert cost == {}

@patch('src.ml_approach_suggestion_agent.agent.MLApproachDecisionAgent.suggest_approach')
def test_execute_task_success(mock_suggest_approach):
    """Test successful execution of the task."""
    agent = MLApproachDecisionAgent()
    mock_response = MethodologyRecommendation(
        selected_methodology="binary_classification",
        justification="The use case is a classic classification problem."
    )
    mock_suggest_approach.return_value = (mock_response, {"cost": 0.1})

    task_data = {
        "domain_name": mock_domain.domain_name,
        "domain_description": mock_domain.domain_description,
        "use_case": mock_use_case,
        "column_descriptions": mock_column_descriptions,
        "column_insights": mock_column_insights,
    }

    result = agent.execute_task(task_data)

    assert result["success"] is True
    assert result["result"]["approach"].selected_methodology == "binary_classification"
    assert result["result"]["cost_summary"] == {"cost": 0.1}
    mock_suggest_approach.assert_called_once_with(
        domain_name=mock_domain.domain_name,
        domain_description=mock_domain.domain_description,
        use_case=mock_use_case,
        column_descriptions=mock_column_descriptions,
        column_insights=mock_column_insights,
    )

@patch('src.ml_approach_suggestion_agent.agent.MLApproachDecisionAgent.suggest_approach')
def test_execute_task_failure(mock_suggest_approach):
    """Test failure during task execution."""
    agent = MLApproachDecisionAgent()
    mock_suggest_approach.return_value = (None, {})

    task_data = {
        "domain_name": mock_domain.domain_name,
        "domain_description": mock_domain.domain_description,
        "use_case": mock_use_case,
        "column_descriptions": mock_column_descriptions,
        "column_insights": mock_column_insights,
    }

    result = agent.execute_task(task_data)

    assert result["success"] is False
    assert result["error"] == "Failed to suggest approach."
    mock_suggest_approach.assert_called_once_with(
        domain_name=mock_domain.domain_name,
        domain_description=mock_domain.domain_description,
        use_case=mock_use_case,
        column_descriptions=mock_column_descriptions,
        column_insights=mock_column_insights,
    )

@patch('sfn_blueprint.WorkflowStorageManager')
@patch('src.ml_approach_suggestion_agent.agent.MLApproachDecisionAgent.suggest_approach')
def test_execute_task_with_storage(mock_suggest_approach, mock_storage_manager):
    """Test task execution with result storage."""
    agent = MLApproachDecisionAgent()
    mock_response = MethodologyRecommendation(
        selected_methodology="binary_classification",
        justification="The use case is a classic classification problem."
    )
    mock_suggest_approach.return_value = (mock_response, {"cost": 0.1})
    
    # Mock the storage manager instance
    mock_storage_instance = MagicMock()
    mock_storage_manager.return_value = mock_storage_instance

    task_data = {
        "domain_name": mock_domain.domain_name,
        "domain_description": mock_domain.domain_description,
        "use_case": mock_use_case,
        "column_descriptions": mock_column_descriptions,
        "column_insights": mock_column_insights,
        "workflow_storage_path": "/tmp/test",
        "workflow_id": "test_workflow"
    }

    result = agent.execute_task(task_data)

    assert result["success"] is True
    mock_storage_instance.save_agent_result.assert_called_once()
    
    # Get the arguments passed to save_agent_result
    _, kwargs = mock_storage_instance.save_agent_result.call_args
    assert kwargs['agent_name'] == "MLApproachDecisionAgent"
    assert kwargs['step_name'] == " "
    assert kwargs['data'] == {"quality_reports": mock_response.model_dump(), "cost_summary": {"cost": 0.1}}

