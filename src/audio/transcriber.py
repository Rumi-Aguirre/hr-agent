import whisper

class Transcriber:
    def __init__(self, model_name: str = "base"):
        self.model = whisper.load_model(model_name)
    
    def transcribe(self, audio_data) -> str:
        if isinstance(audio_data, str):
            return audio_data
        
        result = self.model.transcribe(audio_data)
        return result["text"] 