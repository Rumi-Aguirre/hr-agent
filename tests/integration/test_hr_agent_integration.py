"""Integration tests for the HR agent."""

import pytest
import json
from unittest.mock import mock_open, patch, MagicMock
from src.agent import HRAgent, UserData, ExtractedInfo

@pytest.fixture
def mock_knowledge_base():
    """Create a mock knowledge base."""
    mock_kb = MagicMock()
    mock_kb.assign_random_position.return_value = (
        "test_team",
        "test_role",
        {
            "title": "Test Role",
            "description": "Test role description",
            "department": "test_department"
        }
    )
    mock_kb.get_team_info.return_value = {
        "name": "Test Team",
        "lead": "Test Lead",
        "current_projects": ["Project 1", "Project 2"]
    }
    mock_kb.search.return_value = []
    return mock_kb

class TestHRAgentIntegration:
    """Integration tests for HR agent."""

    @pytest.fixture
    def hr_agent(self, mock_knowledge_base):
        """Create an HR agent instance for testing."""
        with patch('src.knowledge.CompanyKnowledgeBase', return_value=mock_knowledge_base):
            return HRAgent()

    @pytest.fixture
    def mock_hr_components(self):
        """Mock HR agent components."""
        with patch('src.agent.hr_agent.LLMChain') as mock_chain:
            yield {
                'chain': mock_chain.return_value
            }

    def test_full_conversation_flow(self, hr_agent, mock_hr_components):
        """Test a complete conversation flow with the HR agent."""
        # Configure mock responses
        mock_hr_components['chain'].run.side_effect = [
            "¡Hola! ¿Cómo te llamas?",  # Initial greeting
            "Gracias Juan. ¿Cuál es tu edad?",  # After name
            "Perfecto. ¿Qué horario prefieres, mañana o tarde?",  # After age
            "¡Genial! Ya tengo toda la información necesaria. ¡Gracias!"  # After schedule
        ]

        messages = [
            "me llamo Juan",
            "tengo 25 años",
            "prefiero el turno mañana"
        ]

        for message in messages:
            hr_agent.process_message(message)

        # Verify final state
        print(hr_agent.state_manager.get_user_data())
        assert hr_agent.state_manager.is_complete()
        user_data = hr_agent.state_manager.get_user_data()
        assert user_data['first_name'] == "Juan"
        assert user_data['age'] == 25
        assert user_data['preferred_schedule'] == "mañana"
