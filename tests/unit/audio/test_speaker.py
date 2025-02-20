"""Tests for the Speaker class."""

import pytest
from unittest.mock import Mock, patch
from src.audio.speaker import Speaker

@pytest.fixture
def mock_pyttsx3():
    """Create a mock pyttsx3 engine."""
    mock_engine = Mock()
    mock_init = Mock(return_value=mock_engine)
    return mock_init, mock_engine

@pytest.fixture
def speaker(mock_pyttsx3):
    """Create a Speaker instance with mocked pyttsx3."""
    mock_init, _ = mock_pyttsx3
    with patch('src.audio.speaker.pyttsx3.init', mock_init):
        speaker = Speaker()
        yield speaker

class TestSpeaker:
    """Test cases for Speaker."""

    def test_initialization(self, speaker, mock_pyttsx3):
        """Test that Speaker initializes correctly."""
        mock_init, mock_engine = mock_pyttsx3
        
        # Verify engine initialization
        mock_init.assert_called_once()
        assert speaker.engine == mock_engine

    def test_speak(self, speaker, mock_pyttsx3):
        """Test the speak functionality."""
        _, mock_engine = mock_pyttsx3
        test_text = "Hello, world!"

        # Call speak method
        speaker.speak(test_text)

        # Verify text-to-speech operations
        mock_engine.say.assert_called_once_with(test_text)
        mock_engine.runAndWait.assert_called_once()

    def test_speak_empty_text(self, speaker, mock_pyttsx3):
        """Test speaking empty text."""
        _, mock_engine = mock_pyttsx3
        
        # Call speak with empty text
        speaker.speak("")

        # Verify behavior with empty text
        mock_engine.say.assert_called_once_with("")
        mock_engine.runAndWait.assert_called_once()

    def test_speak_special_characters(self, speaker, mock_pyttsx3):
        """Test speaking text with special characters."""
        _, mock_engine = mock_pyttsx3
        test_text = "¡Hola! ¿Cómo estás?"

        # Call speak with special characters
        speaker.speak(test_text)

        # Verify handling of special characters
        mock_engine.say.assert_called_once_with(test_text)
        mock_engine.runAndWait.assert_called_once()
