"""
Nova Prime - Voice Assistant with Extensible Skills System

A stable MVP of a local voice assistant loop with a minimal, extensible plugin (skills) system.
"""

__version__ = "0.1.0"

from .core.voice_loop import VoiceLoop
from .skills.registry import SkillRegistry

__all__ = ["VoiceLoop", "SkillRegistry"]