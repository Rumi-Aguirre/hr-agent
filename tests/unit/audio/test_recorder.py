"""Tests for the AudioRecorder class."""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from src.audio.recorder import AudioRecorder

@pytest.fixture
def mock_pyaudio():
    """Create a mock PyAudio instance."""
    mock = Mock()
    mock.paInt16 = 8  # Mock format constant
    mock.open.return_value = Mock(name="stream")
    return mock

@pytest.fixture
def audio_recorder(mock_pyaudio):
    """Create an AudioRecorder instance with mocked PyAudio."""
    with patch('src.audio.recorder.pyaudio.PyAudio', return_value=mock_pyaudio):
        recorder = AudioRecorder()
        yield recorder

class TestAudioRecorder:
    """Test cases for AudioRecorder."""

    def test_initialization(self, audio_recorder, mock_pyaudio):
        """Test that AudioRecorder initializes with correct parameters."""
        assert audio_recorder.audio_format == mock_pyaudio.paInt16
        assert audio_recorder.channels == 1
        assert audio_recorder.rate == 16000
        assert audio_recorder.chunk == 1024
        assert audio_recorder.audio_interface == mock_pyaudio

    def test_record(self, audio_recorder, mock_pyaudio):
        """Test the recording functionality."""
        # Mock stream read to return some dummy audio data
        mock_stream = mock_pyaudio.open.return_value
        mock_stream.read.return_value = b'\x00\x00' * 1024  # Mock 16-bit audio data

        # Test recording with default duration
        audio_data = audio_recorder.record()

        # Verify stream configuration
        mock_pyaudio.open.assert_called_once_with(
            format=mock_pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )

        # Verify stream operations
        assert mock_stream.read.called
        assert mock_stream.stop_stream.called
        assert mock_stream.close.called

        # Verify audio data format
        assert isinstance(audio_data, np.ndarray)
        assert audio_data.dtype == np.float32

    def test_record_custom_duration(self, audio_recorder, mock_pyaudio):
        """Test recording with custom duration."""
        mock_stream = mock_pyaudio.open.return_value
        mock_stream.read.return_value = b'\x00\x00' * 1024

        # Test with custom duration
        custom_duration = 3
        audio_recorder.record(duration=custom_duration)

        # Calculate expected number of chunks based on duration
        expected_chunks = int(audio_recorder.rate / audio_recorder.chunk * custom_duration)
        assert mock_stream.read.call_count == expected_chunks

    def test_cleanup(self, audio_recorder, mock_pyaudio):
        """Test proper cleanup of resources."""
        audio_recorder.__del__()
        mock_pyaudio.terminate.assert_called_once()

    @pytest.mark.parametrize("duration", [-1, 0])
    def test_invalid_duration(self, audio_recorder, duration):
        """Test handling of invalid duration values."""
        with pytest.raises(ValueError):
            audio_recorder.record(duration=duration) 