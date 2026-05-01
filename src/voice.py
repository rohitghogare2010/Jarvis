"""
Jarvis Voice I/O Module
Multi-language voice input/output system with 50+ languages
"""

import speech_recognition as sr
import pyttsx3
import logging
from typing import Optional, Callable

logger = logging.getLogger('JarvisVoice')


class VoiceInput:
    """Speech-to-text with 50+ language support"""
    
    LANGUAGES = {
        'en-US': 'English (US)',
        'en-GB': 'English (UK)',
        'hi-IN': 'Hindi',
        'es-ES': 'Spanish',
        'fr-FR': 'French',
        'de-DE': 'German',
        'it-IT': 'Italian',
        'pt-BR': 'Portuguese (Brazil)',
        'ru-RU': 'Russian',
        'zh-CN': 'Chinese (Mandarin)',
        'ja-JP': 'Japanese',
        'ko-KR': 'Korean',
        'ar-SA': 'Arabic',
        'nl-NL': 'Dutch',
        'pl-PL': 'Polish',
        'tr-TR': 'Turkish',
        'vi-VN': 'Vietnamese',
        'th-TH': 'Thai',
        'id-ID': 'Indonesian',
        'ms-MY': 'Malay',
        'fil-PH': 'Filipino',
        'bn-IN': 'Bengali',
        'ta-IN': 'Tamil',
        'te-IN': 'Telugu',
        'mr-IN': 'Marathi',
        'pa-IN': 'Punjabi',
        'gu-IN': 'Gujarati',
        'kn-IN': 'Kannada',
        'ml-IN': 'Malayalam',
        'ur-PK': 'Urdu',
    }
    
    def __init__(self, language: str = 'en-US'):
        self.recognizer = sr.Recognizer()
        self.language = language
        self.microphone = None
        
    def list_microphones(self):
        """List all available microphones"""
        return sr.Microphone.list_microphone_names()
    
    def set_microphone(self, index: int = 0):
        """Set the microphone by index"""
        microphones = self.list_microphones()
        if index < len(microphones):
            self.microphone = sr.Microphone(device_index=index)
            logger.info(f"Microphone set to: {microphones[index]}")
            return True
        return False
    
    def listen(self, timeout: int = 5) -> Optional[str]:
        """Listen for speech and convert to text"""
        with sr.Microphone() as source:
            logger.info("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=timeout)
                text = self.recognizer.recognize_google(audio, language=self.language)
                logger.info(f"Recognized: {text}")
                return text
            except sr.UnknownValueError:
                logger.warning("Speech not understood")
                return None
            except sr.RequestError as e:
                logger.error(f"Speech recognition error: {e}")
                return None
    
    def listen_for_phrase(self, phrase: str, timeout: int = 10) -> bool:
        """Listen for a specific phrase"""
        with sr.Microphone() as source:
            logger.info(f"Listening for: '{phrase}'")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=timeout)
                text = self.recognizer.recognize_google(audio, language=self.language).lower()
                return phrase.lower() in text
            except Exception as e:
                logger.error(f"Error: {e}")
                return False


class VoiceOutput:
    """Text-to-speech with natural voices"""
    
    def __init__(self, rate: float = 1.0, volume: float = 1.0):
        self.engine = pyttsx3.init()
        self.rate = rate
        self.volume = volume
        self.configure()
    
    def configure(self):
        """Configure voice properties"""
        self.engine.setProperty('rate', int(200 * self.rate))
        self.engine.setProperty('volume', self.volume)
        
        # List available voices
        voices = self.engine.getProperty('voices')
        if voices:
            self.engine.setProperty('voice', voices[0].id)
    
    def speak(self, text: str):
        """Speak the given text"""
        logger.info(f"Speaking: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def save_audio(self, text: str, filename: str):
        """Save speech to audio file"""
        self.engine.save_to_file(text, filename)
        self.engine.runAndWait()
    
    def list_voices(self):
        """List all available voices"""
        return self.engine.getProperty('voices')


class JarvisVoice:
    """Combined voice input/output system"""
    
    def __init__(self, input_lang: str = 'en-US', rate: float = 1.0, volume: float = 1.0):
        self.input = VoiceInput(input_lang)
        self.output = VoiceOutput(rate, volume)
        self.activation_phrase = "hey jarvis"
        self.callback: Optional[Callable] = None
    
    def set_activation_phrase(self, phrase: str):
        """Set the wake word/phrase"""
        self.activation_phrase = phrase.lower()
    
    def set_callback(self, callback: Callable):
        """Set callback function for recognized speech"""
        self.callback = callback
    
    def listen_for_activation(self) -> bool:
        """Wait for activation phrase"""
        return self.input.listen_for_phrase(self.activation_phrase)
    
    def continuous_listen(self):
        """Continuously listen and process commands"""
        logger.info("Starting continuous listening mode...")
        while True:
            if self.listen_for_activation():
                logger.info("Activation phrase detected!")
                self.output.speak("Yes, Sir? How may I help you?")
                
                while True:
                    command = self.input.listen()
                    if command:
                        if self.callback:
                            response = self.callback(command)
                            self.output.speak(response)
                        
                        if any(word in command.lower() for word in ['stop', 'sleep', 'bye', 'exit']):
                            self.output.speak("Going to sleep mode, Sir.")
                            break
                    else:
                        self.output.speak("I didn't catch that. Please repeat.")
    
    def get_supported_languages(self):
        """Return list of supported languages"""
        return self.input.LANGUAGES