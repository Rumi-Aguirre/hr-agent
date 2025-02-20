"""Shared fixtures for integration tests."""

import pytest
from unittest.mock import Mock, patch
import numpy as np
from src.agent.hr_agent import HRAgent
from src.audio.recorder import AudioRecorder
from src.audio.speaker import Speaker
from src.audio.transcriber import Transcriber

@pytest.fixture
def mock_audio_components():
    """Create mocks for all audio components."""
    # Mock PyAudio
    mock_pyaudio = Mock()
    mock_pyaudio.paInt16 = 8
    mock_stream = Mock()
    mock_stream.read.return_value = b'\x00\x00' * 1024
    mock_pyaudio.open.return_value = mock_stream

    # Mock pyttsx3
    mock_tts_engine = Mock()
    mock_tts_init = Mock(return_value=mock_tts_engine)

    # Mock Whisper
    mock_whisper_model = Mock()
    mock_whisper_model.transcribe.return_value = {"text": "Hello"}
    mock_whisper_load = Mock(return_value=mock_whisper_model)

    with patch.multiple('src.audio.recorder',
                       pyaudio=Mock(PyAudio=Mock(return_value=mock_pyaudio))), \
         patch('src.audio.speaker.pyttsx3.init', mock_tts_init), \
         patch('src.audio.transcriber.whisper.load_model', mock_whisper_load):
        
        yield {
            'pyaudio': mock_pyaudio,
            'stream': mock_stream,
            'tts_engine': mock_tts_engine,
            'whisper_model': mock_whisper_model
        }

@pytest.fixture
def mock_hr_components():
    """Create mocks for HR agent components."""
    # Mock LLM
    mock_llm = Mock()
    mock_llm.return_value = "Mocked response"

    # Mock Memory
    mock_memory = Mock()
    mock_memory.chat_memory.messages = []
    mock_memory.load_memory_variables.return_value = {"chat_history": []}

    # Mock Chain
    mock_chain = Mock()
    mock_chain.run.return_value = "Mocked chain response"

    with patch.multiple('src.agent.hr_agent',
                       Ollama=Mock(return_value=mock_llm),
                       ConversationBufferMemory=Mock(return_value=mock_memory),
                       LLMChain=Mock(return_value=mock_chain)):
        yield {
            'llm': mock_llm,
            'memory': mock_memory,
            'chain': mock_chain
        }

@pytest.fixture
def audio_recorder(mock_audio_components):
    """Create an AudioRecorder instance with mocked dependencies."""
    return AudioRecorder()

@pytest.fixture
def speaker(mock_audio_components):
    """Create a Speaker instance with mocked dependencies."""
    return Speaker()

@pytest.fixture
def transcriber(mock_audio_components):
    """Create a Transcriber instance with mocked dependencies."""
    return Transcriber()

@pytest.fixture
def hr_agent(mock_hr_components):
    """Create an HRAgent instance with mocked dependencies."""
    return HRAgent() 