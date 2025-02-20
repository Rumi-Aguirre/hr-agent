"""Tests for the HRAgent class."""

import pytest
import json
from unittest.mock import Mock, patch, mock_open
from src.agent.hr_agent import HRAgent
from src.agent.models.user_data_model import UserData

@pytest.fixture
def mock_dependencies():
    """Create patches for all external dependencies."""
    mock_llm = Mock(name="mock_llm")
    mock_memory = Mock(name="mock_memory")
    mock_chain = Mock(name="mock_chain")
    mock_state_manager = Mock(name="mock_state_manager")
    mock_conversation_manager = Mock(name="mock_conversation_manager")
    mock_extraction_chain = Mock(name="mock_extraction_chain")
    mock_position_manager = Mock(name="mock_position_manager")
    
    # Configure state manager mock
    mock_state_manager.is_complete.return_value = False
    mock_state_manager.get_current_state.return_value = "Current State"
    mock_state_manager.prepare_context.return_value = "Context"
    mock_state_manager.get_user_data.return_value = {
        "first_name": "Juan",
        "age": 25,
        "preferred_schedule": "mañana"
    }

    mock_position_manager.format_position_info.return_value = "Position Info"
    mock_position_manager.get_position_details.return_value = {
        "team": "Team 1",
        "role": "Developer",
        "department": "technology"
    }
    
    # Configure conversation manager mock
    mock_conversation_manager.generate_response.return_value = "Mocked response"
    mock_conversation_manager.get_conversation_history.return_value = [
        {"type": "human", "content": "Hello"},
        {"type": "ai", "content": "Hi"}
    ]
    
    # Configure extraction chain mock
    mock_extraction_chain.extract.return_value = {
        "first_name": "Juan",
        "age": 25,
        "preferred_schedule": "mañana"
    }
    
    with patch.multiple('src.agent.hr_agent',
                       Ollama=Mock(return_value=mock_llm),
                       ConversationBufferMemory=Mock(return_value=mock_memory),
                       LLMChain=Mock(return_value=mock_chain),
                       StateManager=Mock(return_value=mock_state_manager),
                       ConversationManager=Mock(return_value=mock_conversation_manager),
                       InformationExtractionChain=Mock(return_value=mock_extraction_chain),
                       PositionManager=Mock(return_value=mock_position_manager)):
        yield {
            'llm': mock_llm,
            'memory': mock_memory,
            'chain': mock_chain,
            'state_manager': mock_state_manager,
            'conversation_manager': mock_conversation_manager,
            'extraction_chain': mock_extraction_chain,
            'position_manager': mock_position_manager
        }

@pytest.fixture
def hr_agent(mock_dependencies):
    """Create an HRAgent instance with mocked dependencies."""
    return HRAgent()

class TestHRAgent:
    """Test cases for HRAgent."""

    def test_initialization(self, hr_agent, mock_dependencies):
        """Test that HRAgent initializes correctly."""
        assert hr_agent.llm is mock_dependencies['llm']
        assert hr_agent.state_manager is mock_dependencies['state_manager']
        assert hr_agent.conversation_manager is mock_dependencies['conversation_manager']
        assert hr_agent.extraction_chain is mock_dependencies['extraction_chain']

    def test_create_prompt(self, hr_agent):
        """Test prompt template creation."""
        prompt = hr_agent._create_prompt()
        assert prompt.input_variables == ["chat_history", "context", "current_state", "input", "position_info"]
        assert "chat_history" in prompt.template
        assert "input" in prompt.template
        assert "current_state" in prompt.template
        assert "context" in prompt.template
        assert "position_info" in prompt.template

    class TestProcessMessage:
        """Test cases for process_message method."""

        def test_successful_processing(self, hr_agent, mock_dependencies):
            """Test successful message processing."""
            message = "me llamo Juan, tengo 25 años y prefiero el turno mañana"
            
            response, is_complete = hr_agent.process_message(message)
            
            # Verify extraction
            mock_dependencies['extraction_chain'].extract.assert_called_once_with(message)
            
            # Verify state management
            extracted_info = mock_dependencies['extraction_chain'].extract.return_value
            mock_dependencies['state_manager'].validate_and_store_info.assert_called_once_with(extracted_info)
            mock_dependencies['state_manager'].get_current_state.assert_called_once()
            mock_dependencies['state_manager'].prepare_context.assert_called_once()
            mock_dependencies['state_manager'].is_complete.assert_called_once()
            
            # Verify response generation
            mock_dependencies['conversation_manager'].generate_response.assert_called_once_with(
                message=message,
                current_state="Current State",
                context="Context",
                position_info="Position Info"
            )
            
            assert response == "Mocked response"
            assert is_complete is False

        def test_processing_with_validation_error(self, hr_agent, mock_dependencies):
            """Test message processing with validation error."""
            message = "invalid input"
            mock_dependencies['state_manager'].validate_and_store_info.return_value = "Validation Error"
            
            response, is_complete = hr_agent.process_message(message)
            
            mock_dependencies['state_manager'].prepare_context.assert_called_once_with("Validation Error")
            assert response == "Mocked response"
            assert is_complete is False

        def test_processing_with_no_extracted_info(self, hr_agent, mock_dependencies):
            """Test message processing when no information is extracted."""
            message = "hello"
            mock_dependencies['extraction_chain'].extract.return_value = {}
            
            response, is_complete = hr_agent.process_message(message)
            
            mock_dependencies['state_manager'].validate_and_store_info.assert_not_called()
            assert response == "Mocked response"
            assert is_complete is False

        def test_processing_complete_conversation(self, hr_agent, mock_dependencies):
            """Test message processing when conversation is complete."""
            message = "final message"
            mock_dependencies['state_manager'].is_complete.return_value = True
            
            response, is_complete = hr_agent.process_message(message)
            
            assert response == "Mocked response"
            assert is_complete is True

    class TestSaveConversation:
        """Test cases for save_conversation method."""

        def test_successful_save(self, hr_agent, mock_dependencies):
            """Test successful conversation saving."""
            mock_open_file = mock_open()
            expected_data = {
                "is_complete": False,
                "user_data": {
                    "first_name": "Juan",
                    "age": 25,
                    "preferred_schedule": "mañana"
                },
                "conversation": [
                    {"type": "human", "content": "Hello"},
                    {"type": "ai", "content": "Hi"}
                ],
                "assigned_position": {
                    "team": "Team 1",
                    "role": "Developer",
                    "department": "technology"
                }
            }
            
            with patch('builtins.open', mock_open_file):
                hr_agent.save_conversation("test.json")
            
            # Verify file operations
            mock_open_file.assert_called_once_with("test.json", "w", encoding="utf-8")
            handle = mock_open_file()
            
            # Verify data collection
            mock_dependencies['state_manager'].is_complete.assert_called()
            mock_dependencies['state_manager'].get_user_data.assert_called_once()
            mock_dependencies['conversation_manager'].get_conversation_history.assert_called_once()
            mock_dependencies['position_manager'].get_position_details.assert_called_once()
            
            # Verify JSON content
            written_content = ''.join(call.args[0] for call in handle.write.call_args_list)
            saved_data = json.loads(written_content)
            assert saved_data == expected_data

        def test_save_with_default_path(self, hr_agent):
            """Test conversation saving with default file path."""
            mock_open_file = mock_open()
            
            with patch('builtins.open', mock_open_file):
                hr_agent.save_conversation()
            
            mock_open_file.assert_called_once_with("conversation.json", "w", encoding="utf-8") 