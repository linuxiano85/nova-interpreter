"""Steam integration services."""

import os
import platform

def _steam_root():
    """Detect Steam installation directory."""
    system = platform.system()
    
    if system == "Windows":
        # Common Steam paths on Windows
        paths = [
            os.path.expandvars(r"%PROGRAMFILES%\Steam"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Steam"),
            os.path.expanduser(r"~\AppData\Local\Steam"),
        ]
    elif system == "Darwin":  # macOS
        paths = [
            os.path.expanduser("~/Library/Application Support/Steam"),
            "/Applications/Steam.app",
        ]
    else:  # Linux and others
        paths = [
            os.path.expanduser("~/.steam"),
            os.path.expanduser("~/.local/share/Steam"),
            "/usr/games/steam",
            "/opt/steam",
        ]
    
    for path in paths:
        if os.path.exists(path):
            return path
    
    return None