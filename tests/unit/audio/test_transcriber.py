"""Tests for the Transcriber class."""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from src.audio.transcriber import Transcriber

@pytest.fixture
def mock_whisper():
    """Create a mock Whisper model."""
    mock_model = Mock()
    mock_model.transcribe.return_value = {"text": "Hello, world!"}
    mock_load_model = Mock(return_value=mock_model)
    return mock_load_model, mock_model

@pytest.fixture
def transcriber(mock_whisper):
    """Create a Transcriber instance with mocked Whisper."""
    mock_load_model, _ = mock_whisper
    with patch('src.audio.transcriber.whisper.load_model', mock_load_model):
        transcriber = Transcriber()
        yield transcriber

class TestTranscriber:
    """Test cases for Transcriber."""

    def test_initialization(self, transcriber, mock_whisper):
        """Test that Transcriber initializes correctly."""
        mock_load_model, mock_model = mock_whisper
        
        # Verify model loading
        mock_load_model.assert_called_once_with("base")
        assert transcriber.model == mock_model

    def test_initialization_custom_model(self, mock_whisper):
        """Test initialization with custom model name."""
        mock_load_model, _ = mock_whisper
        
        with patch('src.audio.transcriber.whisper.load_model', mock_load_model):
            transcriber = Transcriber(model_name="medium")
            mock_load_model.assert_called_once_with("medium")

    def test_transcribe(self, transcriber, mock_whisper):
        """Test the transcription functionality."""
        _, mock_model = mock_whisper
        
        # Create dummy audio data
        audio_data = np.zeros(16000, dtype=np.float32)  # 1 second of silence
        
        # Test transcription
        result = transcriber.transcribe(audio_data)
        
        # Verify transcription
        mock_model.transcribe.assert_called_once_with(audio_data)
        assert result == "Hello, world!"

    def test_transcribe_empty_audio(self, transcriber, mock_whisper):
        """Test transcription with empty audio data."""
        _, mock_model = mock_whisper
        mock_model.transcribe.return_value = {"text": ""}
        
        # Create empty audio data
        audio_data = np.array([], dtype=np.float32)
        
        # Test transcription
        result = transcriber.transcribe(audio_data)
        
        # Verify empty result
        assert result == ""

    def test_transcribe_error(self, transcriber, mock_whisper):
        """Test handling of transcription errors."""
        _, mock_model = mock_whisper
        mock_model.transcribe.side_effect = Exception("Transcription failed")
        
        # Create dummy audio data
        audio_data = np.zeros(16000, dtype=np.float32)
        
        # Verify error handling
        with pytest.raises(Exception) as exc_info:
            transcriber.transcribe(audio_data)
        assert str(exc_info.value) == "Transcription failed"
