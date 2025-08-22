"""
Base skill class for Nova Prime voice assistant.

Defines the interface that all skills must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class SkillContext:
    """Context object passed to skills during execution."""
    
    def __init__(self, 
                 user_input: str = "",
                 is_mock: bool = False,
                 config: Optional[Dict[str, Any]] = None):
        self.user_input = user_input
        self.is_mock = is_mock
        self.config = config or {}
        self.session_data = {}  # For storing data during session


class SkillResult:
    """Result object returned by skill execution."""
    
    def __init__(self, 
                 success: bool,
                 message: str = "",
                 data: Optional[Dict[str, Any]] = None,
                 should_speak: bool = True):
        self.success = success
        self.message = message
        self.data = data or {}
        self.should_speak = should_speak


class Skill(ABC):
    """Abstract base class for all Nova Prime skills."""
    
    def __init__(self, name: str):
        self.name = name
        self._intents: List[str] = []
    
    @property
    @abstractmethod
    def intents(self) -> List[str]:
        """List of intent names this skill can handle."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this skill does."""
        pass
    
    @abstractmethod
    def handle(self, 
               intent: str, 
               entities: Dict[str, Any], 
               context: SkillContext) -> SkillResult:
        """
        Handle an intent with extracted entities.
        
        Args:
            intent: The intent name to handle
            entities: Extracted entities from the user input
            context: Execution context
            
        Returns:
            SkillResult with execution results
        """
        pass
    
    def can_handle(self, intent: str) -> bool:
        """Check if this skill can handle the given intent."""
        return intent in self.intents
    
    def validate_entities(self, 
                         intent: str, 
                         entities: Dict[str, Any]) -> bool:
        """
        Validate that required entities are present for the intent.
        Override in subclasses for specific validation.
        """
        return True  # Default: no validation required
    
    def get_help_text(self) -> str:
        """Get help text for this skill. Override in subclasses."""
        return f"{self.name}: {self.description}"