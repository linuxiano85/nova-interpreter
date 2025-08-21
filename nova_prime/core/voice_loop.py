"""
Main voice loop for Nova Prime voice assistant.

Implements the pipeline: Hotword -> STT -> Intent router -> Skill execution -> TTS
"""

import logging
import os
import signal
import sys
import time
from typing import Optional, Dict, Any

from .providers import HotwordProvider, STTProvider, TTSProvider, create_default_providers
from .intent_router import IntentRouter
from ..skills.registry import SkillRegistry
from ..skills.base import SkillContext


class VoiceLoop:
    """Main voice loop coordinator for Nova Prime."""
    
    def __init__(self, 
                 hotword_provider: Optional[HotwordProvider] = None,
                 stt_provider: Optional[STTProvider] = None,
                 tts_provider: Optional[TTSProvider] = None,
                 intent_router: Optional[IntentRouter] = None,
                 skill_registry: Optional[SkillRegistry] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the voice loop.
        
        Args:
            hotword_provider: Provider for hotword detection
            stt_provider: Provider for speech-to-text
            tts_provider: Provider for text-to-speech
            intent_router: Router for intent recognition
            skill_registry: Registry of available skills
            config: Configuration dictionary
        """
        self.config = config or {}
        self._setup_logging()
        
        # Initialize providers
        if hotword_provider or stt_provider or tts_provider:
            self.hotword_provider = hotword_provider
            self.stt_provider = stt_provider
            self.tts_provider = tts_provider
        else:
            # Create default providers
            mock_mode = self._should_use_mock()
            providers = create_default_providers(mock=mock_mode)
            self.hotword_provider, self.stt_provider, self.tts_provider = providers
        
        # Initialize components
        self.intent_router = intent_router or IntentRouter()
        self.skill_registry = skill_registry or SkillRegistry()
        
        # State
        self._running = False
        self._setup_signal_handlers()
        
        # Load skills
        self._load_skills()
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = self.config.get("log_level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger("nova_prime.voice_loop")
    
    def _should_use_mock(self) -> bool:
        """Determine if we should use mock providers."""
        return (
            self.config.get("mock", False) or
            self.config.get("no_audio", False) or
            os.getenv("NOVA_PRIME_MOCK", "").lower() in ("1", "true", "yes") or
            os.getenv("NOVA_PRIME_NO_AUDIO", "").lower() in ("1", "true", "yes") or
            os.getenv("CI", "").lower() in ("1", "true", "yes")
        )
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _load_skills(self) -> None:
        """Load all available skills."""
        mock_mode = self._should_use_mock()
        user_skills_dir = self.config.get("user_skills_dir")
        
        self.logger.info("Loading skills...")
        self.skill_registry.discover_and_load_skills(
            mock_mode=mock_mode,
            user_skills_dir=user_skills_dir
        )
        
        skills_info = self.skill_registry.get_skills_info()
        self.logger.info(f"Loaded {len(skills_info)} skills: {list(skills_info.keys())}")
    
    def start(self) -> None:
        """Start the voice loop."""
        if self._running:
            self.logger.warning("Voice loop is already running")
            return
        
        self._running = True
        self.logger.info("Starting Nova Prime voice loop...")
        
        try:
            # Start hotword detection
            self.hotword_provider.start()
            self.logger.info("Hotword detection started")
            
            self._main_loop()
            
        except Exception as e:
            self.logger.error(f"Error in voice loop: {e}")
            raise
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop the voice loop."""
        if not self._running:
            return
        
        self.logger.info("Stopping Nova Prime voice loop...")
        self._running = False
        
        try:
            self.hotword_provider.stop()
        except Exception as e:
            self.logger.error(f"Error stopping hotword provider: {e}")
    
    def _main_loop(self) -> None:
        """Main voice processing loop."""
        while self._running:
            try:
                # Wait for hotword
                self.logger.debug("Waiting for hotword...")
                hotword_timeout = self.config.get("hotword_timeout", 30.0)
                
                if self.hotword_provider.wait_for_hotword(timeout=hotword_timeout):
                    self.logger.info("Hotword detected!")
                    self._process_voice_input()
                else:
                    self.logger.debug("Hotword timeout, continuing...")
                
                # Brief pause between iterations
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                self.logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(1)  # Brief pause before retrying
    
    def _process_voice_input(self) -> None:
        """Process a single voice input after hotword detection."""
        try:
            # Listen for speech
            self.logger.debug("Listening for speech...")
            stt_timeout = self.config.get("stt_timeout", 5.0)
            
            transcript = self.stt_provider.listen(timeout=stt_timeout)
            if not transcript:
                self.logger.warning("No speech detected")
                self._speak("I didn't hear anything. Please try again.")
                return
            
            self.logger.info(f"Transcript: {transcript}")
            
            # Route intent
            intent, entities = self.intent_router.route_intent(transcript)
            if not intent:
                self.logger.warning(f"No intent found for: {transcript}")
                self._speak("I'm not sure how to help with that.")
                return
            
            self.logger.info(f"Intent: {intent}, Entities: {entities}")
            
            # Execute skill
            context = SkillContext(
                user_input=transcript,
                is_mock=self._should_use_mock(),
                config=self.config
            )
            
            result = self.skill_registry.execute_intent(intent, entities, context)
            if not result:
                self.logger.warning(f"No skill found for intent: {intent}")
                self._speak("I don't know how to do that yet.")
                return
            
            # Handle result
            self._handle_skill_result(result)
            
        except Exception as e:
            self.logger.error(f"Error processing voice input: {e}")
            self._speak("Sorry, I encountered an error processing your request.")
    
    def _handle_skill_result(self, result) -> None:
        """Handle the result from skill execution."""
        self.logger.info(f"Skill result: success={result.success}, message='{result.message}'")
        
        if result.should_speak and result.message:
            self._speak(result.message)
        
        # Log additional data if present
        if result.data:
            self.logger.debug(f"Skill data: {result.data}")
    
    def _speak(self, text: str) -> None:
        """Speak text using TTS provider."""
        try:
            self.tts_provider.speak(text)
        except Exception as e:
            self.logger.error(f"Error speaking text '{text}': {e}")
    
    def process_single_utterance(self, text: str) -> Dict[str, Any]:
        """
        Process a single text utterance (for testing/CLI use).
        
        Args:
            text: Text to process
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Route intent
            intent, entities = self.intent_router.route_intent(text)
            
            result_data = {
                "input": text,
                "intent": intent,
                "entities": entities,
                "success": False,
                "message": "",
                "skill_data": {}
            }
            
            if not intent:
                result_data["message"] = "No intent found"
                return result_data
            
            # Execute skill
            context = SkillContext(
                user_input=text,
                is_mock=self._should_use_mock(),
                config=self.config
            )
            
            skill_result = self.skill_registry.execute_intent(intent, entities, context)
            if not skill_result:
                result_data["message"] = "No skill found for intent"
                return result_data
            
            # Update result data
            result_data.update({
                "success": skill_result.success,
                "message": skill_result.message,
                "skill_data": skill_result.data
            })
            
            return result_data
            
        except Exception as e:
            return {
                "input": text,
                "intent": None,
                "entities": {},
                "success": False,
                "message": f"Error: {str(e)}",
                "skill_data": {}
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the voice loop."""
        return {
            "running": self._running,
            "skills_loaded": len(self.skill_registry.get_all_skills()),
            "supported_intents": self.skill_registry.get_supported_intents(),
            "mock_mode": self._should_use_mock(),
            "config": self.config
        }