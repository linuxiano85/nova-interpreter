"""
Skill registry for Nova Prime voice assistant.

Manages discovery and loading of both builtin and user skills.
"""

import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Type
import platformdirs

from .base import Skill, SkillContext, SkillResult


class SkillRegistry:
    """Registry for managing Nova Prime skills."""
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.intent_to_skill: Dict[str, Skill] = {}
    
    def discover_and_load_skills(self, 
                                mock_mode: bool = False,
                                user_skills_dir: Optional[str] = None) -> None:
        """
        Discover and load all available skills.
        
        Args:
            mock_mode: Whether to run in mock mode
            user_skills_dir: Optional custom user skills directory
        """
        # Load builtin skills
        self._load_builtin_skills(mock_mode)
        
        # Load user skills
        self._load_user_skills(user_skills_dir, mock_mode)
        
        # Build intent mapping
        self._build_intent_mapping()
    
    def _load_builtin_skills(self, mock_mode: bool = False) -> None:
        """Load builtin skills from nova_prime.skills.builtin."""
        builtin_dir = Path(__file__).parent / "builtin"
        
        if not builtin_dir.exists():
            return
        
        for skill_file in builtin_dir.glob("*.py"):
            if skill_file.name.startswith("_"):
                continue
            
            try:
                self._load_skill_from_file(skill_file, f"nova_prime.skills.builtin.{skill_file.stem}")
            except Exception as e:
                print(f"Warning: Failed to load builtin skill {skill_file.name}: {e}")
    
    def _load_user_skills(self, 
                         user_skills_dir: Optional[str] = None,
                         mock_mode: bool = False) -> None:
        """Load user skills from user directory."""
        if user_skills_dir:
            skills_dir = Path(user_skills_dir)
        else:
            # Use platformdirs to get user config directory
            app_name = "Nova Prime"
            config_dir = Path(platformdirs.user_config_dir(app_name))
            skills_dir = config_dir / "skills"
        
        if not skills_dir.exists():
            # Don't error if user skills directory doesn't exist
            return
        
        for skill_file in skills_dir.glob("*.py"):
            if skill_file.name.startswith("_"):
                continue
            
            try:
                self._load_skill_from_file(skill_file, None)
            except Exception as e:
                print(f"Warning: Failed to load user skill {skill_file.name}: {e}")
    
    def _load_skill_from_file(self, skill_file: Path, module_name: Optional[str] = None) -> None:
        """Load a skill from a Python file."""
        if module_name:
            # Load as module
            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                print(f"Warning: Could not import {module_name}: {e}")
                return
        else:
            # Load from file path
            spec = importlib.util.spec_from_file_location(skill_file.stem, skill_file)
            if not spec or not spec.loader:
                return
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        
        # Find skill classes in the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                issubclass(attr, Skill) and 
                attr != Skill):
                
                try:
                    skill_instance = attr()
                    self.register_skill(skill_instance)
                except Exception as e:
                    print(f"Warning: Failed to instantiate skill {attr_name}: {e}")
    
    def register_skill(self, skill: Skill) -> None:
        """Register a skill instance."""
        self.skills[skill.name] = skill
        
        # Register intents
        for intent in skill.intents:
            if intent in self.intent_to_skill:
                print(f"Warning: Intent '{intent}' is already handled by skill '{self.intent_to_skill[intent].name}'. "
                      f"Overriding with skill '{skill.name}'.")
            self.intent_to_skill[intent] = skill
    
    def _build_intent_mapping(self) -> None:
        """Build mapping from intents to skills."""
        self.intent_to_skill.clear()
        for skill in self.skills.values():
            for intent in skill.intents:
                self.intent_to_skill[intent] = skill
    
    def get_skill_for_intent(self, intent: str) -> Optional[Skill]:
        """Get the skill that handles the given intent."""
        return self.intent_to_skill.get(intent)
    
    def execute_intent(self, 
                      intent: str, 
                      entities: Dict[str, any], 
                      context: SkillContext) -> Optional[SkillResult]:
        """
        Execute an intent using the appropriate skill.
        
        Args:
            intent: Intent name to execute
            entities: Extracted entities
            context: Execution context
            
        Returns:
            SkillResult if a skill was found and executed, None otherwise
        """
        skill = self.get_skill_for_intent(intent)
        if not skill:
            return None
        
        if not skill.validate_entities(intent, entities):
            return SkillResult(
                success=False,
                message=f"Invalid entities for intent '{intent}'"
            )
        
        try:
            return skill.handle(intent, entities, context)
        except Exception as e:
            return SkillResult(
                success=False,
                message=f"Error executing skill '{skill.name}': {str(e)}"
            )
    
    def get_all_skills(self) -> List[Skill]:
        """Get list of all registered skills."""
        return list(self.skills.values())
    
    def get_skill_by_name(self, name: str) -> Optional[Skill]:
        """Get a skill by name."""
        return self.skills.get(name)
    
    def get_supported_intents(self) -> List[str]:
        """Get list of all supported intents."""
        return list(self.intent_to_skill.keys())
    
    def get_skills_info(self) -> Dict[str, Dict[str, any]]:
        """Get information about all registered skills."""
        info = {}
        for skill in self.skills.values():
            info[skill.name] = {
                "description": skill.description,
                "intents": skill.intents,
                "help": skill.get_help_text()
            }
        return info