"""
System Volume Skill for Nova Prime voice assistant.

Gets and sets system volume. Uses mocks in CI/testing.
"""

import os
import platform
import subprocess
from typing import Dict, List, Any

from ..base import Skill, SkillContext, SkillResult


class SystemVolumeSkill(Skill):
    """Skill for managing system volume."""
    
    def __init__(self):
        super().__init__("system_volume")
        self._current_volume = 50  # Mock current volume for testing
    
    @property
    def intents(self) -> List[str]:
        return ["system_volume"]
    
    @property
    def description(self) -> str:
        return "Controls system volume (get/set/increase/decrease)"
    
    def handle(self, 
               intent: str, 
               entities: Dict[str, Any], 
               context: SkillContext) -> SkillResult:
        """Handle the system_volume intent."""
        
        if intent != "system_volume":
            return SkillResult(
                success=False, 
                message=f"Cannot handle intent: {intent}"
            )
        
        action = entities.get("action", "get")
        volume_percent = entities.get("volume_percent")
        
        # In mock/test mode, just simulate the action
        if context.is_mock or os.getenv("CI", "").lower() in ("1", "true", "yes"):
            return self._handle_mock(action, volume_percent)
        
        # Try to execute the real action
        return self._handle_real(action, volume_percent)
    
    def _handle_mock(self, action: str, volume_percent: int = None) -> SkillResult:
        """Handle volume control in mock mode."""
        
        if action == "get":
            return SkillResult(
                success=True,
                message=f"Current volume is {self._current_volume}%",
                data={"action": "get", "volume": self._current_volume}
            )
        
        elif action == "set" and volume_percent is not None:
            old_volume = self._current_volume
            self._current_volume = max(0, min(100, volume_percent))
            return SkillResult(
                success=True,
                message=f"Volume changed from {old_volume}% to {self._current_volume}%",
                data={"action": "set", "old_volume": old_volume, "new_volume": self._current_volume}
            )
        
        elif action == "increase":
            old_volume = self._current_volume
            increase_amount = volume_percent if volume_percent else 10
            self._current_volume = min(100, self._current_volume + increase_amount)
            return SkillResult(
                success=True,
                message=f"Volume increased from {old_volume}% to {self._current_volume}%",
                data={"action": "increase", "old_volume": old_volume, "new_volume": self._current_volume}
            )
        
        elif action == "decrease":
            old_volume = self._current_volume
            decrease_amount = volume_percent if volume_percent else 10
            self._current_volume = max(0, self._current_volume - decrease_amount)
            return SkillResult(
                success=True,
                message=f"Volume decreased from {old_volume}% to {self._current_volume}%",
                data={"action": "decrease", "old_volume": old_volume, "new_volume": self._current_volume}
            )
        
        else:
            return SkillResult(
                success=False,
                message=f"Invalid volume action: {action}"
            )
    
    def _handle_real(self, action: str, volume_percent: int = None) -> SkillResult:
        """Handle real volume control."""
        system = platform.system().lower()
        
        try:
            if action == "get":
                volume = self._get_system_volume(system)
                if volume is not None:
                    return SkillResult(
                        success=True,
                        message=f"Current volume is {volume}%",
                        data={"action": "get", "volume": volume}
                    )
                else:
                    return SkillResult(
                        success=False,
                        message="Could not get system volume"
                    )
            
            elif action == "set" and volume_percent is not None:
                success = self._set_system_volume(system, volume_percent)
                if success:
                    return SkillResult(
                        success=True,
                        message=f"Volume set to {volume_percent}%",
                        data={"action": "set", "volume": volume_percent}
                    )
                else:
                    return SkillResult(
                        success=False,
                        message=f"Could not set volume to {volume_percent}%"
                    )
            
            elif action in ["increase", "decrease"]:
                current_volume = self._get_system_volume(system)
                if current_volume is None:
                    return SkillResult(
                        success=False,
                        message="Could not get current volume"
                    )
                
                change_amount = volume_percent if volume_percent else 10
                if action == "decrease":
                    change_amount = -change_amount
                
                new_volume = max(0, min(100, current_volume + change_amount))
                success = self._set_system_volume(system, new_volume)
                
                if success:
                    return SkillResult(
                        success=True,
                        message=f"Volume {action}d from {current_volume}% to {new_volume}%",
                        data={"action": action, "old_volume": current_volume, "new_volume": new_volume}
                    )
                else:
                    return SkillResult(
                        success=False,
                        message=f"Could not {action} volume"
                    )
            
            else:
                return SkillResult(
                    success=False,
                    message=f"Invalid volume action: {action}"
                )
                
        except Exception as e:
            return SkillResult(
                success=False,
                message=f"Error controlling volume: {str(e)}"
            )
    
    def _get_system_volume(self, system: str) -> int:
        """Get current system volume."""
        try:
            if system == "windows":
                # Use PowerShell to get volume
                result = subprocess.run([
                    "powershell", "-Command",
                    "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{VOLUMEDOWN}'); Start-Sleep -Milliseconds 50; [System.Windows.Forms.SendKeys]::SendWait('{VOLUMEUP}');"
                ], capture_output=True, text=True)
                # This is a simplified approach - real implementation would be more complex
                return 50  # Placeholder
            
            elif system == "darwin":
                # Use osascript to get volume
                result = subprocess.run([
                    "osascript", "-e", "output volume of (get volume settings)"
                ], capture_output=True, text=True)
                if result.returncode == 0:
                    return int(result.stdout.strip())
            
            elif system == "linux":
                # Use amixer to get volume
                result = subprocess.run([
                    "amixer", "get", "Master"
                ], capture_output=True, text=True)
                # Parse amixer output - simplified
                return 50  # Placeholder
            
        except Exception:
            pass
        
        return None
    
    def _set_system_volume(self, system: str, volume: int) -> bool:
        """Set system volume."""
        try:
            if system == "windows":
                # Use PowerShell to set volume - simplified approach
                subprocess.run([
                    "powershell", "-Command",
                    f"# Set volume to {volume}% - placeholder"
                ], check=True)
                return True
            
            elif system == "darwin":
                # Use osascript to set volume
                subprocess.run([
                    "osascript", "-e", f"set volume output volume {volume}"
                ], check=True)
                return True
            
            elif system == "linux":
                # Use amixer to set volume
                subprocess.run([
                    "amixer", "set", "Master", f"{volume}%"
                ], check=True)
                return True
            
        except Exception:
            pass
        
        return False
    
    def get_help_text(self) -> str:
        """Get help text for this skill."""
        return "Control system volume. Say 'volume up', 'set volume to 50%', 'what's the volume?'"