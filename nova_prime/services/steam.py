import os
import platform
import re
import subprocess
from typing import Dict, Optional

def _steam_root() -> Optional[str]:
    """Find Steam installation directory."""
    system = platform.system().lower()
    if "darwin" in system:
        p = os.path.expanduser("~/Library/Application Support/Steam")
        return p if os.path.isdir(p) else None
    elif "windows" in system:
        candidates = [
            os.path.expandvars(r"%PROGRAMFILES(x86)%\Steam"),
            os.path.expandvars(r"%PROGRAMFILES%\Steam"),
            os.path.expandvars(r"%LOCALAPPDATA%\Steam")
        ]
        for c in candidates:
            if c and os.path.isdir(c):
                return c
        return None
    else:
        p = os.path.expanduser("~/.local/share/Steam")
        return p if os.path.isdir(p) else None

def _steamapps_dir() -> Optional[str]:
    """Find Steam apps directory."""
    root = _steam_root()
    if not root:
        return None
    sa = os.path.join(root, "steamapps")
    return sa if os.path.isdir(sa) else None

def _parse_appmanifest(path: str) -> Optional[Dict[str, str]]:
    """Parse Steam app manifest file to extract appid and name."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        appid_match = re.search(r'"appid"\s+"(\d+)"', content)
        name_match = re.search(r'"name"\s+"([^"]+)"', content)
        if appid_match and name_match:
            return {"appid": appid_match.group(1), "name": name_match.group(1)}
    except Exception:
        pass
    return None

def installed_games() -> Dict[str, str]:
    """
    Get mapping of installed Steam games (name -> appid).
    
    Returns:
        Dict[str, str]: Mapping of lowercase game names to appids
    """
    mapping: Dict[str, str] = {}
    sa = _steamapps_dir()
    if not sa:
        return mapping
    try:
        for fn in os.listdir(sa):
            if fn.startswith("appmanifest_") and fn.endswith(".acf"):
                meta = _parse_appmanifest(os.path.join(sa, fn))
                if meta:
                    mapping[meta["name"].lower()] = meta["appid"]
    except Exception:
        pass
    return mapping

def launch_game_by_name(name: str) -> bool:
    """
    Launch a Steam game by name.
    
    Args:
        name (str): Game name (case-insensitive, supports partial matching)
        
    Returns:
        bool: True if game was found and launch attempted, False otherwise
    """
    games = installed_games()
    appid = games.get(name.lower())
    if not appid:
        # Try partial matching
        for n, aid in games.items():
            if name.lower() in n:
                appid = aid
                break
    if not appid:
        return False
    return launch_game_by_appid(appid)

def launch_game_by_appid(appid: str) -> bool:
    """
    Launch a Steam game by AppID.
    
    Args:
        appid (str): Steam AppID
        
    Returns:
        bool: True if launch was attempted, False otherwise
    """
    system = platform.system().lower()
    try:
        steam_url = f"steam://rungameid/{appid}"
        if "darwin" in system:
            subprocess.Popen(["open", steam_url])
            return True
        elif "windows" in system:
            subprocess.Popen(["cmd", "/c", f"start {steam_url}"], shell=True)
            return True
        else:
            subprocess.Popen(["xdg-open", steam_url])
            return True
    except Exception:
        return False