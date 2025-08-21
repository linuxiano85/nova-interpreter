"""
Provider interfaces for voice assistant components.

Defines abstract protocols for Hotword detection, Speech-to-Text, and Text-to-Speech.
"""

import os
from abc import ABC, abstractmethod
from typing import Optional, Iterator


class HotwordProvider(ABC):
    """Abstract interface for hotword detection providers."""
    
    @abstractmethod
    def start(self) -> None:
        """Start hotword detection."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop hotword detection."""
        pass
    
    @abstractmethod
    def wait_for_hotword(self, timeout: Optional[float] = None) -> bool:
        """Wait for hotword detection. Returns True if detected, False if timeout."""
        pass


class STTProvider(ABC):
    """Abstract interface for Speech-to-Text providers."""
    
    @abstractmethod
    def transcribe(self, audio_data: bytes) -> str:
        """Transcribe audio data to text."""
        pass
    
    @abstractmethod
    def listen(self, timeout: Optional[float] = None) -> Optional[str]:
        """Listen for speech and return transcribed text."""
        pass


class TTSProvider(ABC):
    """Abstract interface for Text-to-Speech providers."""
    
    @abstractmethod
    def speak(self, text: str) -> None:
        """Convert text to speech and play it."""
        pass


# Mock implementations for CI/testing
class MockHotwordProvider(HotwordProvider):
    """Mock hotword provider for testing."""
    
    def __init__(self, auto_trigger: bool = True):
        self.auto_trigger = auto_trigger
        self._running = False
        self._triggered = False
    
    def start(self) -> None:
        self._running = True
        if self.auto_trigger:
            self._triggered = True
    
    def stop(self) -> None:
        self._running = False
    
    def wait_for_hotword(self, timeout: Optional[float] = None) -> bool:
        if self._triggered:
            self._triggered = False  # Reset for next call
            return True
        return False


class MockSTTProvider(STTProvider):
    """Mock STT provider for testing."""
    
    def __init__(self, mock_transcription: str = "apri calcolatrice"):
        self.mock_transcription = mock_transcription
    
    def transcribe(self, audio_data: bytes) -> str:
        return self.mock_transcription
    
    def listen(self, timeout: Optional[float] = None) -> Optional[str]:
        return self.mock_transcription


class MockTTSProvider(TTSProvider):
    """Mock TTS provider for testing."""
    
    def __init__(self):
        self.spoken_texts = []
    
    def speak(self, text: str) -> None:
        print(f"[TTS] {text}")
        self.spoken_texts.append(text)


def create_default_providers(mock: bool = None) -> tuple[HotwordProvider, STTProvider, TTSProvider]:
    """Create default provider instances based on environment and availability."""
    
    # Check if we should use mocks
    use_mock = (
        mock is True or 
        os.getenv("NOVA_PRIME_MOCK", "").lower() in ("1", "true", "yes") or
        os.getenv("NOVA_PRIME_NO_AUDIO", "").lower() in ("1", "true", "yes") or
        os.getenv("CI", "").lower() in ("1", "true", "yes")
    )
    
    if use_mock:
        return (
            MockHotwordProvider(),
            MockSTTProvider(),
            MockTTSProvider()
        )
    
    # Try to create real providers with fallback to mocks
    hotword_provider = _create_hotword_provider()
    stt_provider = _create_stt_provider()
    tts_provider = _create_tts_provider()
    
    return hotword_provider, stt_provider, tts_provider


def _create_hotword_provider() -> HotwordProvider:
    """Create a real hotword provider or fallback to mock."""
    try:
        import openwakeword
        
        class OpenWakeWordProvider(HotwordProvider):
            def __init__(self):
                self.model = None
                self._running = False
            
            def start(self) -> None:
                if not self._running:
                    self.model = openwakeword.Model()
                    self._running = True
            
            def stop(self) -> None:
                self._running = False
                self.model = None
            
            def wait_for_hotword(self, timeout: Optional[float] = None) -> bool:
                # Simplified implementation - in real use would listen to audio
                return False
        
        return OpenWakeWordProvider()
    except ImportError:
        return MockHotwordProvider()


def _create_stt_provider() -> STTProvider:
    """Create a real STT provider or fallback to mock."""
    try:
        import faster_whisper
        
        class FasterWhisperProvider(STTProvider):
            def __init__(self):
                self.model = None
            
            def transcribe(self, audio_data: bytes) -> str:
                if not self.model:
                    self.model = faster_whisper.WhisperModel("tiny")
                # Simplified implementation - would process audio_data
                return "mock transcription from faster_whisper"
            
            def listen(self, timeout: Optional[float] = None) -> Optional[str]:
                # Simplified implementation - would record and transcribe
                return self.transcribe(b"")
        
        return FasterWhisperProvider()
    except ImportError:
        return MockSTTProvider()


def _create_tts_provider() -> TTSProvider:
    """Create a real TTS provider or fallback to mock."""
    try:
        import pyttsx3
        
        class Pyttsx3Provider(TTSProvider):
            def __init__(self):
                self.engine = None
            
            def speak(self, text: str) -> None:
                if not self.engine:
                    self.engine = pyttsx3.init()
                self.engine.say(text)
                self.engine.runAndWait()
        
        return Pyttsx3Provider()
    except ImportError:
        return MockTTSProvider()