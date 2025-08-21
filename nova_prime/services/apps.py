import os
import platform
import subprocess
import shutil

def open_app(app_name: str) -> bool:
    """
    Open a system application by name across OSes.
    - macOS: open -a "App Name"
    - Windows: Start-Process via PowerShell / cmd start
    - Linux: try gtk-launch with .desktop ID, xdg-open if path, else PATH lookup
    
    Args:
        app_name (str): Name of the application to open
        
    Returns:
        bool: True if launch was attempted, False otherwise
    """
    system = platform.system().lower()
    try:
        if "darwin" in system:
            subprocess.Popen(["open", "-a", app_name])
            return True
        elif "windows" in system:
            cmd = [
                "powershell", "-NoProfile", "-Command",
                f"Start-Process -FilePath '{app_name}'"
            ]
            try:
                subprocess.Popen(cmd, creationflags=subprocess.DETACHED_PROCESS)
                return True
            except Exception:
                subprocess.Popen(["cmd", "/c", "start", "", app_name], shell=True)
                return True
        else:
            # Linux
            desktop_id = app_name.lower().replace(" ", "-") + ".desktop"
            if shutil.which("gtk-launch"):
                ret = subprocess.call(["gtk-launch", desktop_id])
                if ret == 0:
                    return True
            if os.path.exists(app_name):
                subprocess.Popen(["xdg-open", app_name])
                return True
            exe = shutil.which(app_name)
            if exe:
                subprocess.Popen([exe])
                return True
        return False
    except Exception:
        return False