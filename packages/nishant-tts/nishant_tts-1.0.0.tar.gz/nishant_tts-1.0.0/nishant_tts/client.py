import modal
import os
import time

f5_service = modal.Cls.from_name("f5-tts-backend", "F5Inference")

class VoiceManager:
    def __init__(self):
        self.app = f5_service()

    def create_voice(self, voice_name: str, audio_path: str):
        start_time = time.time()
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        print(f"Uploading and processing voice '{voice_name}'...")
        
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
            
        self.app.register_voice.remote(voice_name, audio_bytes)
        
        elapsed = time.time() - start_time
        print(f"Voice '{voice_name}' registered successfully! Time taken: {elapsed:.2f}s")

    def speak(self, text: str, voice_name: str, output_file: str = "output.wav"):
        start_time = time.time()
        print(f"Generating speech for: '{text}' using voice: {voice_name}")
        
        wav_bytes = self.app.generate.remote(text, voice_name)
        
        with open(output_file, "wb") as f:
            f.write(wav_bytes)
            
        elapsed = time.time() - start_time
        print(f"Saved to {output_file}. Time taken: {elapsed:.2f}s")

_manager = VoiceManager()
create_voice = _manager.create_voice
speak = _manager.speak
