"""Integration tests for audio components."""

import pytest
import numpy as np
from unittest.mock import Mock

class TestAudioIntegration:
    """Integration tests for audio components."""

    def test_recording_to_transcription(self, audio_recorder, transcriber, mock_audio_components):
        """Test the flow from recording to transcription."""
        # Configure mock audio data
        mock_audio_components['stream'].read.return_value = b'\x00\x00' * 1024
        mock_audio_components['whisper_model'].transcribe.return_value = {
            "text": "me llamo Juan y tengo 25 años"
        }

        # Record audio
        audio_data = audio_recorder.record(duration=3)
        
        # Verify audio data format
        assert isinstance(audio_data, np.ndarray)
        assert audio_data.dtype == np.float32
        
        # Transcribe the recorded audio
        transcribed_text = transcriber.transcribe(audio_data)
        
        # Verify transcription
        assert transcribed_text == "me llamo Juan y tengo 25 años"
        mock_audio_components['whisper_model'].transcribe.assert_called_once_with(audio_data)

    def test_text_to_speech(self, speaker, mock_audio_components):
        """Test the text-to-speech conversion."""
        test_text = "¡Hola! ¿Cómo estás?"
        
        # Speak the text
        speaker.speak(test_text)
        
        # Verify TTS operations
        mock_audio_components['tts_engine'].say.assert_called_once_with(test_text)
        mock_audio_components['tts_engine'].runAndWait.assert_called_once()

    def test_full_audio_pipeline(self, audio_recorder, transcriber, speaker, mock_audio_components):
        """Test the complete audio pipeline: recording -> transcription -> speech."""
        # Configure mocks
        mock_audio_components['stream'].read.return_value = b'\x00\x00' * 1024
        mock_audio_components['whisper_model'].transcribe.return_value = {
            "text": "me llamo Juan"
        }

        # Record audio
        audio_data = audio_recorder.record(duration=2)
        
        # Transcribe
        transcribed_text = transcriber.transcribe(audio_data)
        assert transcribed_text == "me llamo Juan"
        
        # Generate response
        response = "¡Hola Juan!"
        
        # Speak response
        speaker.speak(response)
        
        # Verify complete pipeline
        mock_audio_components['whisper_model'].transcribe.assert_called_once()
        mock_audio_components['tts_engine'].say.assert_called_once_with(response)
        mock_audio_components['tts_engine'].runAndWait.assert_called_once() 