"""
Open App Skill for Nova Prime voice assistant.

Resolves and launches known applications. Uses no-op in CI/testing.
"""

import os
import platform
import subprocess
from typing import Dict, List, Any

from ..base import Skill, SkillContext, SkillResult


class OpenAppSkill(Skill):
    """Skill for opening/launching applications."""
    
    def __init__(self):
        super().__init__("open_app")
        self._app_commands = self._get_app_commands()
    
    @property
    def intents(self) -> List[str]:
        return ["open_app"]
    
    @property
    def description(self) -> str:
        return "Opens applications by name (e.g., 'open calculator', 'apri calcolatrice')"
    
    def _get_app_commands(self) -> Dict[str, Dict[str, str]]:
        """Get platform-specific app launch commands."""
        system = platform.system().lower()
        
        commands = {
            "calculator": {
                "windows": "calc.exe",
                "darwin": "open -a Calculator",
                "linux": "gnome-calculator || kcalc || xcalc"
            },
            "notepad": {
                "windows": "notepad.exe",
                "darwin": "open -a TextEdit", 
                "linux": "gedit || kate || nano"
            },
            "browser": {
                "windows": "start msedge || start chrome || start firefox",
                "darwin": "open -a Safari || open -a Chrome || open -a Firefox",
                "linux": "firefox || google-chrome || chromium-browser"
            },
            "chrome": {
                "windows": "start chrome",
                "darwin": "open -a 'Google Chrome'",
                "linux": "google-chrome || chromium-browser"
            },
            "firefox": {
                "windows": "start firefox",
                "darwin": "open -a Firefox",
                "linux": "firefox"
            },
            "edge": {
                "windows": "start msedge",
                "darwin": "open -a 'Microsoft Edge'",
                "linux": "microsoft-edge || microsoft-edge-beta"
            }
        }
        
        return commands
    
    def handle(self, 
               intent: str, 
               entities: Dict[str, Any], 
               context: SkillContext) -> SkillResult:
        """Handle the open_app intent."""
        
        if intent != "open_app":
            return SkillResult(
                success=False, 
                message=f"Cannot handle intent: {intent}"
            )
        
        app_name = entities.get("app_name", "").lower()
        original_name = entities.get("original_name", app_name)
        
        if not app_name:
            return SkillResult(
                success=False,
                message="No application name specified"
            )
        
        # In mock/test mode, just return a plan without executing
        if context.is_mock or os.getenv("CI", "").lower() in ("1", "true", "yes"):
            return self._handle_mock(app_name, original_name)
        
        # Try to launch the app
        return self._launch_app(app_name, original_name)
    
    def _handle_mock(self, app_name: str, original_name: str) -> SkillResult:
        """Handle app opening in mock mode."""
        if app_name in self._app_commands:
            return SkillResult(
                success=True,
                message=f"Would open {original_name} ({app_name})",
                data={"action": "open_app", "app": app_name, "original": original_name}
            )
        else:
            return SkillResult(
                success=False,
                message=f"Unknown application: {original_name}",
                data={"action": "open_app", "app": app_name, "original": original_name}
            )
    
    def _launch_app(self, app_name: str, original_name: str) -> SkillResult:
        """Actually launch the application."""
        if app_name not in self._app_commands:
            return SkillResult(
                success=False,
                message=f"I don't know how to open '{original_name}'"
            )
        
        system = platform.system().lower()
        app_commands = self._app_commands[app_name]
        
        command = app_commands.get(system)
        if not command:
            return SkillResult(
                success=False,
                message=f"'{original_name}' is not supported on {platform.system()}"
            )
        
        try:
            # Execute the command
            if system == "windows":
                subprocess.run(command, shell=True, check=False)
            else:
                subprocess.run(command, shell=True, check=False)
            
            return SkillResult(
                success=True,
                message=f"Opening {original_name}",
                data={"action": "open_app", "app": app_name, "command": command}
            )
            
        except Exception as e:
            return SkillResult(
                success=False,
                message=f"Failed to open {original_name}: {str(e)}"
            )
    
    def validate_entities(self, intent: str, entities: Dict[str, Any]) -> bool:
        """Validate that app_name is present."""
        return "app_name" in entities
    
    def get_help_text(self) -> str:
        """Get help text for this skill."""
        apps = list(self._app_commands.keys())
        return f"Open applications. Supported apps: {', '.join(apps)}"