import whisper
import pyttsx3
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import os

class VoiceIO:
    def __init__(self, language=None):
        self.model = whisper.load_model("base")
        self.engine = pyttsx3.init()
        self.language = language
        self.voices = self.engine.getProperty('voices')

    def set_character_voice(self, character):
        """
        Sets the voice based on character age, gender, and type.
        """
        # In a real professional app, we'd use Coqui TTS or similar for unique voices.
        # Here we map to available system voices as a fallback.
        gender_map = {
            "male": 0,
            "female": 1
        }
        
        voice_index = gender_map.get(character.gender.lower(), 0)
        if voice_index < len(self.voices):
            self.engine.setProperty('voice', self.voices[voice_index].id)
        
        # Adjust rate and pitch based on age (simulated)
        if character.age < 12:
            self.engine.setProperty('rate', 200) # Faster for kids
        elif character.age > 60:
            self.engine.setProperty('rate', 150) # Slower for elderly
        else:
            self.engine.setProperty('rate', 175)

    def generate_character_audio(self, text, character):
        """
        Generates unique audio for a specific character.
        """
        self.set_character_voice(character)
        # In a high-end system, this would return a file path to a generated .wav file
        # using a professional AI voice model.
        self.speak(text)
        return f"Audio generated for {character.name}"

    def record_audio(self, duration=5, fs=44100):
        print("Recording...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        print("Done recording.")
        write('output.wav', fs, recording)
        return 'output.wav'

    def transcribe(self, audio_path):
        result = self.model.transcribe(audio_path, language=self.language)
        return result['text'], result['language']

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
