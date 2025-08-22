"""Tests for Nova Prime skills discovery and loading."""

import pytest
import tempfile
import os
from pathlib import Path

from nova_prime.skills.registry import SkillRegistry
from nova_prime.skills.base import Skill, SkillContext, SkillResult
from nova_prime.skills.builtin.open_app import OpenAppSkill
from nova_prime.skills.builtin.system_volume import SystemVolumeSkill


class TestSkillsDiscovery:
    """Test skills discovery and loading."""
    
    def test_builtin_skills_loaded(self):
        """Test that builtin skills are loaded correctly."""
        registry = SkillRegistry()
        registry.discover_and_load_skills(mock_mode=True)
        
        skills = registry.get_all_skills()
        skill_names = [skill.name for skill in skills]
        
        # Check that builtin skills are present
        assert "open_app" in skill_names
        assert "system_volume" in skill_names
        
        # Check skills have correct properties
        open_app_skill = registry.get_skill_by_name("open_app")
        assert open_app_skill is not None
        assert isinstance(open_app_skill, OpenAppSkill)
        assert "open_app" in open_app_skill.intents
        
        volume_skill = registry.get_skill_by_name("system_volume")
        assert volume_skill is not None
        assert isinstance(volume_skill, SystemVolumeSkill)
        assert "system_volume" in volume_skill.intents
    
    def test_user_skills_directory_absent(self):
        """Test that missing user skills directory is tolerated."""
        registry = SkillRegistry()
        
        # Should not raise an exception
        registry._load_user_skills("/nonexistent/directory", mock_mode=True)
        
        # Should still have builtin skills
        registry._load_builtin_skills(mock_mode=True)
        skills = registry.get_all_skills()
        assert len(skills) >= 2
    
    def test_custom_user_skill_loading(self):
        """Test loading a custom user skill."""
        # Create a temporary directory with a custom skill
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_file = Path(temp_dir) / "test_skill.py"
            skill_content = '''
from nova_prime.skills.base import Skill, SkillContext, SkillResult
from typing import Dict, List, Any

class TestSkill(Skill):
    def __init__(self):
        super().__init__("test_skill")
    
    @property
    def intents(self) -> List[str]:
        return ["test_intent"]
    
    @property
    def description(self) -> str:
        return "A test skill"
    
    def handle(self, intent: str, entities: Dict[str, Any], context: SkillContext) -> SkillResult:
        return SkillResult(success=True, message="Test skill executed")
'''
            skill_file.write_text(skill_content)
            
            # Load skills from the temporary directory
            registry = SkillRegistry()
            registry._load_user_skills(temp_dir, mock_mode=True)
            
            # Check that the test skill was loaded
            test_skill = registry.get_skill_by_name("test_skill")
            assert test_skill is not None
            assert "test_intent" in test_skill.intents
    
    def test_intent_to_skill_mapping(self):
        """Test that intent-to-skill mapping works correctly."""
        registry = SkillRegistry()
        registry.discover_and_load_skills(mock_mode=True)
        
        # Test mapping for builtin skills
        open_app_skill = registry.get_skill_for_intent("open_app")
        assert open_app_skill is not None
        assert open_app_skill.name == "open_app"
        
        volume_skill = registry.get_skill_for_intent("system_volume")
        assert volume_skill is not None
        assert volume_skill.name == "system_volume"
        
        # Test non-existent intent
        unknown_skill = registry.get_skill_for_intent("unknown_intent")
        assert unknown_skill is None
    
    def test_skill_execution_through_registry(self):
        """Test executing skills through the registry."""
        registry = SkillRegistry()
        registry.discover_and_load_skills(mock_mode=True)
        
        # Test open_app execution
        context = SkillContext(user_input="apri calcolatrice", is_mock=True)
        result = registry.execute_intent(
            "open_app",
            {"app_name": "calculator", "original_name": "calcolatrice"},
            context
        )
        
        assert result is not None
        assert result.success is True
        assert "calculator" in result.message.lower()
        
        # Test system_volume execution
        result = registry.execute_intent(
            "system_volume",
            {"action": "set", "volume_percent": 50},
            context
        )
        
        assert result is not None
        assert result.success is True
        assert "50" in result.message
    
    def test_skills_info_generation(self):
        """Test generation of skills information."""
        registry = SkillRegistry()
        registry.discover_and_load_skills(mock_mode=True)
        
        skills_info = registry.get_skills_info()
        
        assert "open_app" in skills_info
        assert "system_volume" in skills_info
        
        open_app_info = skills_info["open_app"]
        assert "description" in open_app_info
        assert "intents" in open_app_info
        assert "help" in open_app_info
        assert "open_app" in open_app_info["intents"]
    
    def test_skill_validation(self):
        """Test skill entity validation."""
        registry = SkillRegistry()
        registry.discover_and_load_skills(mock_mode=True)
        
        open_app_skill = registry.get_skill_by_name("open_app")
        
        # Valid entities
        valid_entities = {"app_name": "calculator", "original_name": "calc"}
        assert open_app_skill.validate_entities("open_app", valid_entities) is True
        
        # Invalid entities (missing app_name)
        invalid_entities = {"original_name": "calc"}
        assert open_app_skill.validate_entities("open_app", invalid_entities) is False
    
    def test_broken_skill_handling(self):
        """Test that broken user skills don't crash the system."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a broken skill file
            skill_file = Path(temp_dir) / "broken_skill.py"
            skill_content = '''
# This is a broken skill file with syntax errors
class BrokenSkill(Skill:  # Missing closing parenthesis
    def __init__(self):
        super().__init__("broken")
    
    # Missing required methods
'''
            skill_file.write_text(skill_content)
            
            # Should not raise an exception, just print warnings
            registry = SkillRegistry()
            registry._load_user_skills(temp_dir, mock_mode=True)
            
            # Should still work with builtin skills
            registry._load_builtin_skills(mock_mode=True)
            skills = registry.get_all_skills()
            assert len(skills) >= 2  # Builtin skills still loaded