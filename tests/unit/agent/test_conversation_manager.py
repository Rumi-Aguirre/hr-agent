"""Tests for the ConversationManager class."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.agent.conversation_manager import ConversationManager
from langchain.schema import HumanMessage, AIMessage

# Create a patch for each dependency
@pytest.fixture
def patches():
    """Create patches for all external dependencies."""
    mock_llm = Mock(name="mock_llm")
    mock_memory = Mock(name="mock_memory")
    mock_chain = Mock(name="mock_chain")
    
    # Configure memory mock
    mock_memory.chat_memory.messages = []
    mock_memory.load_memory_variables.return_value = {"chat_history": []}
    
    # Configure chain mock
    mock_chain.run.return_value = "Mocked response"
    
    patches = {
        'langchain.llms.Ollama': mock_llm,
        'langchain.memory.ConversationBufferMemory': mock_memory,
        'langchain.chains.LLMChain': mock_chain
    }
    
    with patch.multiple('src.agent.conversation_manager', **{
        'Ollama': Mock(return_value=mock_llm),
        'ConversationBufferMemory': Mock(return_value=mock_memory),
        'LLMChain': Mock(return_value=mock_chain)
    }):
        yield {
            'llm': mock_llm,
            'memory': mock_memory,
            'chain': mock_chain
        }

@pytest.fixture
def conversation_manager(patches):
    """Create a ConversationManager instance with mocked dependencies."""
    return ConversationManager()

class TestConversationManager:
    """Test cases for ConversationManager."""

    def test_initialization(self, conversation_manager, patches):
        """Test that ConversationManager initializes correctly."""
        assert conversation_manager.llm is patches['llm']
        assert conversation_manager.memory is patches['memory']
        assert conversation_manager.conversation is patches['chain']


    def test_create_prompt(self, conversation_manager):
        prompt = conversation_manager._create_prompt()
        assert prompt.input_variables == ["chat_history", "context", "current_state", "input", "position_info"]
        assert "chat_history" in prompt.template
        assert "input" in prompt.template
        assert "current_state" in prompt.template
        assert "context" in prompt.template

    class TestFormatChatHistory:
        def test_empty_history(self, conversation_manager, patches):
            patches['memory'].load_memory_variables.return_value = {"chat_history": []}
            assert conversation_manager.format_chat_history() == ""

        def test_single_message(self, conversation_manager, patches):
            patches['memory'].load_memory_variables.return_value = {
                "chat_history": [HumanMessage(content="Hello")]
            }
            assert conversation_manager.format_chat_history() == "Human: Hello\\n"

        def test_multiple_messages(self, conversation_manager, patches):
            patches['memory'].load_memory_variables.return_value = {
                "chat_history": [
                    HumanMessage(content="Hello"),
                    AIMessage(content="Hi there"),
                    HumanMessage(content="How are you?")
                ]
            }
            expected = "Human: Hello\\nAssistant: Hi there\\nHuman: How are you?\\n"
            assert conversation_manager.format_chat_history() == expected

    class TestGenerateResponse:
        def test_response_generation(self, conversation_manager, patches):
            message = "Hello"
            current_state = "Empty state"
            context = "Test context"
            position_info = "Test position info"

            response = conversation_manager.generate_response(message, current_state, context, position_info)
            
            # Verify chain was called correctly
            patches['chain'].run.assert_called_once()
            call_kwargs = patches['chain'].run.call_args[1]
            assert call_kwargs["input"] == message
            assert call_kwargs["current_state"] == current_state
            assert call_kwargs["context"] == context
            assert call_kwargs["position_info"] == position_info
            assert isinstance(call_kwargs["chat_history"], str)
            
            # Verify response
            assert response == "Mocked response"

        def test_memory_update(self, conversation_manager, patches):
            message = "Hello"
            current_state = "Empty state"
            context = "Test context"
            position_info = "Test position info"
            conversation_manager.generate_response(message, current_state, context, position_info)
            
            # Verify memory was updated
            patches['memory'].save_context.assert_called_once_with(
                {"input": message},
                {"output": "Mocked response"}
            )

        @pytest.mark.parametrize("message,current_state,context,position_info", [
            ("", "", "", ""),
            ("Hello", None, None, None),
            ("¡Hola!", "Estado actual", "Contexto", "Posición actual"),
            ("Test " * 100, "Long state", "Long context", "Long position info"),
        ])
        def test_input_variations(self, conversation_manager, patches, message, current_state, context, position_info):
            response = conversation_manager.generate_response(message, current_state, context, position_info)
            assert response == "Mocked response"
            patches['chain'].run.assert_called_once()

    class TestGetConversationHistory:
        def test_empty_history(self, conversation_manager, patches):
            patches['memory'].chat_memory.messages = []
            history = conversation_manager.get_conversation_history()
            assert history == []

        def test_single_message_history(self, conversation_manager, patches):
            patches['memory'].chat_memory.messages = [HumanMessage(content="Hello")]
            history = conversation_manager.get_conversation_history()
            assert len(history) == 1
            assert history[0] == {"type": "human", "content": "Hello"}

        def test_multiple_message_history(self, conversation_manager, patches):
            patches['memory'].chat_memory.messages = [
                HumanMessage(content="Hello"),
                AIMessage(content="Hi there"),
                HumanMessage(content="How are you?")
            ]
            history = conversation_manager.get_conversation_history()
            assert len(history) == 3
            assert history[0] == {"type": "human", "content": "Hello"}
            assert history[1] == {"type": "ai", "content": "Hi there"}
            assert history[2] == {"type": "human", "content": "How are you?"} 
