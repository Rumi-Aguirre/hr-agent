import pyaudio
import numpy as np
import platform
import subprocess
import shutil

class AudioRecorder:
    def __init__(self):
        self.has_audio_system = self._check_input_devices()
        if not self.has_audio_system:
            print("❌ No se encontró un sistema de entrada de audio disponible")
        else :
            self.audio_format = pyaudio.paInt16
            self.channels = 1
            self.rate = 16000
            self.chunk = 1024
            self.audio_interface = pyaudio.PyAudio()

    def record(self, duration=5):
        if not self.has_audio_system:
            print("\n💬 Por favor, ingresa tu mensaje (presiona Enter para enviar):")
            user_input = input("> ").strip()
            return user_input
        
        if duration <= 0:
            raise ValueError("Duration must be greater than 0")
            
        print("🎤 Grabando...")
        stream = self.audio_interface.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        frames = []
        for _ in range(0, int(self.rate / self.chunk * duration)):
            data = stream.read(self.chunk)
            frames.append(data)
            
        stream.stop_stream()
        stream.close()
        print("✅ Grabación finalizada")
        
        # Convert to normalized float32 array
        audio_data = np.frombuffer(b"".join(frames), dtype=np.int16).astype(np.float32) / 32768.0
        return audio_data

    def __del__(self):
        if self.has_audio_system:
            self.audio_interface.terminate()

    def _check_input_devices(self) -> bool:
        system = platform.system()
        
        if system == "Darwin":  # macOS
            try:
                result = subprocess.run(['system_profiler', 'SPAudioDataType'], 
                                     capture_output=True, text=True)
                if 'Input Source' in result.stdout:
                    return True
                return False
            except FileNotFoundError:
                return False
        else:  # Linux
            if shutil.which('arecord'):
                devices = subprocess.check_output(['arecord', '-l'], stderr=subprocess.PIPE).decode()
                if len(devices.strip()) > 0:
                    return True
            
            if shutil.which('pactl'):
                try:
                    sources = subprocess.check_output(['pactl', 'list', 'sources'], stderr=subprocess.PIPE).decode()
                    if len(sources.strip()) > 0:
                        return True
                except subprocess.CalledProcessError:
                    print("error pactl")
            
            try:
                p = pyaudio.PyAudio()
                input_devices = []
                
                for i in range(p.get_device_count()):
                    try:
                        device_info = p.get_device_info_by_index(i)
                        if device_info['maxInputChannels'] > 0:
                            input_devices.append(device_info)
                            print(f"  - Dispositivo {i}: {device_info['name']}")
                    except Exception as e:
                        print("error pyaudio")
                
                p.terminate()
                
                if input_devices:
                    return True
                else:
                    return False
                    
            except Exception as e:
                print(f"⚠️ Error al verificar dispositivos PyAudio: {e}")
                return False