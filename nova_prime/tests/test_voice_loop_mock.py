"""Tests for Nova Prime voice loop mock functionality."""

import pytest
import os
from unittest.mock import patch

from nova_prime.core.voice_loop import VoiceLoop
from nova_prime.core.providers import MockHotwordProvider, MockSTTProvider, MockTTSProvider
from nova_prime.core.intent_router import IntentRouter
from nova_prime.skills.registry import SkillRegistry
from nova_prime.skills.base import SkillContext


class TestVoiceLoopMock:
    """Test voice loop with mock providers."""
    
    def setup_method(self):
        """Setup test environment."""
        # Force mock mode
        self.config = {
            "mock": True,
            "log_level": "DEBUG"
        }
        
        # Create mock providers
        self.hotword_provider = MockHotwordProvider(auto_trigger=True)
        self.stt_provider = MockSTTProvider(mock_transcription="apri calcolatrice")
        self.tts_provider = MockTTSProvider()
        
        # Create voice loop with mock providers
        self.voice_loop = VoiceLoop(
            hotword_provider=self.hotword_provider,
            stt_provider=self.stt_provider,
            tts_provider=self.tts_provider,
            config=self.config
        )
    
    def test_voice_loop_initialization(self):
        """Test that voice loop initializes correctly."""
        assert self.voice_loop is not None
        assert self.voice_loop.hotword_provider is not None
        assert self.voice_loop.stt_provider is not None
        assert self.voice_loop.tts_provider is not None
        assert self.voice_loop.intent_router is not None
        assert self.voice_loop.skill_registry is not None
    
    def test_skills_loaded(self):
        """Test that builtin skills are loaded."""
        skills = self.voice_loop.skill_registry.get_all_skills()
        skill_names = [skill.name for skill in skills]
        
        assert "open_app" in skill_names
        assert "system_volume" in skill_names
    
    def test_process_single_utterance_open_app(self):
        """Test processing 'apri calcolatrice' utterance."""
        result = self.voice_loop.process_single_utterance("apri calcolatrice")
        
        assert result["success"] is True
        assert result["intent"] == "open_app"
        assert result["entities"]["app_name"] == "calculator"
        assert "calculator" in result["message"].lower()
    
    def test_process_single_utterance_open_app_english(self):
        """Test processing 'open calculator' utterance."""
        result = self.voice_loop.process_single_utterance("open calculator")
        
        assert result["success"] is True
        assert result["intent"] == "open_app"
        assert result["entities"]["app_name"] == "calculator"
        assert "calculator" in result["message"].lower()
    
    def test_process_single_utterance_volume(self):
        """Test processing volume command."""
        result = self.voice_loop.process_single_utterance("set volume to 75%")
        
        assert result["success"] is True
        assert result["intent"] == "system_volume"
        assert result["entities"]["action"] == "set"
        assert result["entities"]["volume_percent"] == 75
    
    def test_process_single_utterance_no_intent(self):
        """Test processing utterance with no matching intent."""
        result = self.voice_loop.process_single_utterance("this is not a valid command")
        
        assert result["success"] is False
        assert result["intent"] is None
        assert "No intent found" in result["message"]
    
    def test_mock_providers_behavior(self):
        """Test that mock providers behave correctly."""
        # Test hotword provider
        self.hotword_provider.start()
        assert self.hotword_provider.wait_for_hotword() is True
        
        # Test STT provider
        transcript = self.stt_provider.listen()
        assert transcript == "apri calcolatrice"
        
        # Test TTS provider
        self.tts_provider.speak("test message")
        assert "test message" in self.tts_provider.spoken_texts
    
    def test_intent_routing(self):
        """Test intent routing functionality."""
        router = self.voice_loop.intent_router
        
        # Test Italian
        intent, entities = router.route_intent("apri calcolatrice")
        assert intent == "open_app"
        assert entities["app_name"] == "calculator"
        
        # Test English
        intent, entities = router.route_intent("open calculator")
        assert intent == "open_app"
        assert entities["app_name"] == "calculator"
        
        # Test volume
        intent, entities = router.route_intent("volume up")
        assert intent == "system_volume"
        assert entities["action"] == "increase"
    
    def test_skill_registry_discovery(self):
        """Test skill registry discovery."""
        registry = SkillRegistry()
        registry.discover_and_load_skills(mock_mode=True)
        
        skills = registry.get_all_skills()
        assert len(skills) >= 2  # At least open_app and system_volume
        
        # Test intent execution
        context = SkillContext(user_input="apri calcolatrice", is_mock=True)
        result = registry.execute_intent(
            "open_app", 
            {"app_name": "calculator", "original_name": "calcolatrice"}, 
            context
        )
        
        assert result is not None
        assert result.success is True
        assert "calculator" in result.message.lower()


class TestVoiceLoopEnvironment:
    """Test voice loop environment detection."""
    
    def test_mock_mode_detection_ci(self):
        """Test that CI environment triggers mock mode."""
        with patch.dict(os.environ, {"CI": "true"}):
            voice_loop = VoiceLoop()
            assert voice_loop._should_use_mock() is True
    
    def test_mock_mode_detection_no_audio(self):
        """Test that NOVA_PRIME_NO_AUDIO triggers mock mode."""
        with patch.dict(os.environ, {"NOVA_PRIME_NO_AUDIO": "1"}):
            voice_loop = VoiceLoop()
            assert voice_loop._should_use_mock() is True
    
    def test_mock_mode_detection_mock_env(self):
        """Test that NOVA_PRIME_MOCK triggers mock mode."""
        with patch.dict(os.environ, {"NOVA_PRIME_MOCK": "yes"}):
            voice_loop = VoiceLoop()
            assert voice_loop._should_use_mock() is True