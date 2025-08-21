import sys
import threading
from typing import Optional, Dict

def configure_interpreter_os_mode():
    """Configure Open Interpreter for OS mode."""
    try:
        from interpreter import interpreter as oi
        oi.reset()
        oi.auto_run = True
        try:
            oi.os = True
        except Exception:
            pass
        return oi
    except ImportError:
        return None

def handle_text_command(text: str, state, tr: Dict[str, str]):
    """
    Handle text commands with direct app/Steam actions, fallback to Open Interpreter.
    
    Args:
        text (str): User input text
        state: UI state object
        tr (Dict[str, str]): Translations
    """
    from nova_prime.services.apps import open_app
    from nova_prime.services.steam import launch_game_by_name
    
    lower = text.strip().lower()
    
    # Handle Steam game launching
    if lower.startswith("apri steam") or lower.startswith("open steam") or lower.startswith("avvia steam"):
        parts = lower.split("steam", 1)
        if len(parts) > 1 and parts[1].strip():
            game = parts[1].strip().strip(":").strip()
            if launch_game_by_name(game):
                state.set_status(tr["status.ready"])
                return
        else:
            if open_app("Steam"):
                state.set_status(tr["status.ready"])
                return
    
    # Handle app launching
    if lower.startswith("apri ") or lower.startswith("avvia ") or lower.startswith("open "):
        target = text.split(" ", 1)[1].strip()
        if open_app(target):
            state.set_status(tr["status.ready"])
            return

    # Fallback to Open Interpreter OS mode
    _oi = configure_interpreter_os_mode()
    if _oi:
        try:
            for _ in _oi.chat(text, stream=True, display=False):
                pass
        except Exception:
            pass
    
    state.set_status(tr["status.ready"])

def main():
    """
    Main entry point for Nova Prime.
    
    Note: This is a placeholder implementation. The actual implementation
    requires the PySide6 package which is only installed with [nova-prime] extras.
    """
    print("Nova Prime")
    print("=" * 50)
    
    try:
        from nova_prime.config import ConfigStore
        from nova_prime.i18n import load_translations
        
        cfg = ConfigStore().load()
        tr = load_translations(cfg.language)
        
        print(f"Language: {cfg.language}")
        print(f"Wake word: {cfg.wake_word}")
        print(f"Hotkey: {cfg.global_hotkey}")
        print()
        
        # Try to import PySide6 for GUI
        try:
            from PySide6.QtCore import QUrl, QObject, Signal, Property, Slot
            from PySide6.QtGui import QGuiApplication
            from PySide6.QtQml import QQmlApplicationEngine
            
            # Full GUI implementation would go here
            print("PySide6 available - GUI mode would be enabled")
            print("Note: Full GUI implementation requires additional setup")
            
        except ImportError:
            print("PySide6 not available. Install with: pip install 'open-interpreter[nova-prime]'")
            print()
            print("Running in CLI mode...")
            
            # Simple CLI loop for testing
            while True:
                try:
                    user_input = input(f"{tr['status.ready']}\n> ")
                    if user_input.lower() in ['exit', 'quit', 'q']:
                        break
                    
                    print(f"{tr['status.thinking']}")
                    
                    # Create dummy state object for testing
                    class DummyState:
                        def set_status(self, status):
                            print(f"Status: {status}")
                    
                    state = DummyState()
                    handle_text_command(user_input, state, tr)
                    
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure nova_prime package is properly installed")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())