from src.audio.recorder import AudioRecorder
from src.audio.speaker import Speaker
from src.audio.transcriber import Transcriber
from src.agent.hr_agent import HRAgent
from src.config.settings import Settings
import warnings
from src.agent.field_names import FIELD_NAMES

warnings.filterwarnings('ignore') 

class ConversationalAgent:
    def __init__(self):
        print("Inicializando componentes...")
        print("> Inicializando settings")
        self.settings = Settings()
        print("> Inicializando audio recorder")
        self.recorder = AudioRecorder()
        print("> Inicializando speaker")
        self.speaker = Speaker()
        print("> Inicializando transcriber")
        self.transcriber = Transcriber(model_name=self.settings.WHISPER_MODEL)
        print("> Inicializando hr_agent")
        self.hr_agent = HRAgent(model_name=self.settings.LLM_MODEL)

    def _handle_audio_input(self) -> str:
        """Handle audio recording and transcription."""
        audio_data = self.recorder.record(duration=self.settings.DEFAULT_RECORDING_DURATION)
        text = self.transcriber.transcribe(audio_data).lower().strip()
        print(f"🎯 Transcripción: {text}")
        return text

    def _handle_response(self, response: str):
        """Handle system response output."""
        print(f"🤖 {response}")
        self.speaker.speak(response)

    def _handle_user_exit(self):
        """Handle user exit command."""
        if (self.hr_agent.state_manager.is_complete()):
            print("\n✨ ¡Genial! He recopilado toda la información necesaria:")
            for field, value in self.hr_agent.state_manager.user_data.model_dump(exclude_none=True).items():
                print(f"📝 {FIELD_NAMES[field]}: {value}")
        else:
            print("\n⚠️ No se recopiló toda la información necesaria.")
            
        self.hr_agent.save_conversation()
        print("\n💾 Información guardada exitosamente.")
                

    def run(self):
        print("🤖 Iniciando agente de RRHH...")
        print("💡 Di 'salir' o 'terminar' en cualquier momento para finalizar.")
        
        # Initial greeting
        initial_response, _ = self.hr_agent.process_message("")
        self._handle_response(initial_response)
        
        while True:
            user_input = self._handle_audio_input()
            
            # Check for exit command
            if user_input in ["salir", "terminar"]:
                self._handle_user_exit()
                break
            
            response, is_complete = self.hr_agent.process_message(user_input)
            
            self._handle_response(response)
            
            if is_complete:
                self._handle_user_exit()
                break

        print("👋 Gracias por usar el agente de RRHH")

def main():
    agent = ConversationalAgent()
    agent.run()

if __name__ == "__main__":
    main() 