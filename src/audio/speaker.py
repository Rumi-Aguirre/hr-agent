import pyttsx3
import subprocess
import shutil
import platform

class Speaker:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.system = platform.system()
        self.has_audio_system = self.check_audio_system()
        if not self.has_audio_system:
            print("❌ No se encontró un sistema de audio disponible")
        
    def speak(self, text):
        if self.has_audio_system:
            self.engine.say(text)
            self.engine.runAndWait() 
        else:
            print(text)

    def check_audio_system(self) -> bool:
        if self.system == "Darwin":
            return self.check_macos_audio()
        else:
            return self.check_linux_audio()
    
    def check_macos_audio(self) -> bool:
        try:
            subprocess.run(['afplay', '--help'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except FileNotFoundError:
            return False
    
    def check_linux_audio(self) -> bool:
        if shutil.which('aplay'):
            try:
                devices = subprocess.check_output(['aplay', '-l'], stderr=subprocess.PIPE).decode()
                return len(devices) > 0
            except subprocess.CalledProcessError:
                return False
            
        return False
            