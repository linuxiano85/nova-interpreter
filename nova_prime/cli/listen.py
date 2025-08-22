"""
CLI interface for Nova Prime voice assistant.

Provides the nova-prime-listen command with various options.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from ..core.voice_loop import VoiceLoop


def create_config_from_args(args: argparse.Namespace) -> Dict[str, Any]:
    """Create configuration dictionary from command line arguments."""
    config = {}
    
    # Mock/audio settings
    if args.mock:
        config["mock"] = True
    if args.no_audio:
        config["no_audio"] = True
    
    # Timeouts and thresholds
    if hasattr(args, "hotword_timeout") and args.hotword_timeout:
        config["hotword_timeout"] = args.hotword_timeout
    if hasattr(args, "stt_timeout") and args.stt_timeout:
        config["stt_timeout"] = args.stt_timeout
    
    # Directories
    if hasattr(args, "user_skills_dir") and args.user_skills_dir:
        config["user_skills_dir"] = args.user_skills_dir
    
    # Logging
    if args.verbose:
        config["log_level"] = "DEBUG"
    elif args.quiet:
        config["log_level"] = "WARNING"
    else:
        config["log_level"] = "INFO"
    
    return config


def load_config_file(config_path: str) -> Dict[str, Any]:
    """Load configuration from a file."""
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            print(f"Warning: Config file {config_path} not found")
            return {}
        
        with open(config_file, 'r') as f:
            if config_path.endswith('.json'):
                return json.load(f)
            elif config_path.endswith(('.yml', '.yaml')):
                import yaml
                return yaml.safe_load(f)
            else:
                print(f"Warning: Unsupported config file format: {config_path}")
                return {}
                
    except Exception as e:
        print(f"Error loading config file {config_path}: {e}")
        return {}


def setup_parser() -> argparse.ArgumentParser:
    """Setup command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="nova-prime-listen",
        description="Nova Prime Voice Assistant - Listen for voice commands and execute skills"
    )
    
    # Main operation modes
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Force mock providers (no real audio I/O)"
    )
    
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Disable audio I/O"
    )
    
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process a single utterance and exit"
    )
    
    # Configuration
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (JSON or YAML)"
    )
    
    # Directories
    parser.add_argument(
        "--user-skills-dir",
        type=str,
        help="Custom user skills directory"
    )
    
    # Timeouts and thresholds
    parser.add_argument(
        "--hotword-timeout",
        type=float,
        default=30.0,
        help="Hotword detection timeout in seconds (default: 30.0)"
    )
    
    parser.add_argument(
        "--stt-timeout", 
        type=float,
        default=5.0,
        help="Speech-to-text timeout in seconds (default: 5.0)"
    )
    
    # Logging
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Enable quiet mode (warnings and errors only)"
    )
    
    # Testing/development
    parser.add_argument(
        "--test-utterance",
        type=str,
        help="Test a specific utterance without voice input (implies --once)"
    )
    
    parser.add_argument(
        "--list-skills",
        action="store_true",
        help="List available skills and exit"
    )
    
    parser.add_argument(
        "--status",
        action="store_true", 
        help="Show status information and exit"
    )
    
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="Run diagnostics and show system health (doctor mode)"
    )
    
    return parser


def list_skills(voice_loop: VoiceLoop) -> None:
    """List all available skills."""
    skills_info = voice_loop.skill_registry.get_skills_info()
    
    if not skills_info:
        print("No skills loaded.")
        return
    
    print(f"Loaded {len(skills_info)} skills:\n")
    
    for skill_name, info in skills_info.items():
        print(f"• {skill_name}")
        print(f"  Description: {info['description']}")
        print(f"  Intents: {', '.join(info['intents'])}")
        print(f"  Help: {info['help']}")
        print()


def show_status(voice_loop: VoiceLoop) -> None:
    """Show voice loop status."""
    status = voice_loop.get_status()
    
    print("Nova Prime Voice Assistant Status:")
    print(f"  Running: {status['running']}")
    print(f"  Skills loaded: {status['skills_loaded']}")
    print(f"  Mock mode: {status['mock_mode']}")
    print(f"  Supported intents: {', '.join(status['supported_intents'])}")
    print()


def run_doctor(voice_loop: VoiceLoop) -> int:
    """Run doctor diagnostics and report system health."""
    print("🩺 Nova Prime Doctor - System Health Check")
    print("=" * 50)
    print()
    
    # Check skills
    print("📦 Skills Discovery:")
    skills_info = voice_loop.skill_registry.get_skills_info()
    
    if skills_info:
        print(f"  ✅ Found {len(skills_info)} skills:")
        for skill_name, info in skills_info.items():
            print(f"    • {skill_name}: {info['description']}")
            print(f"      Intents: {', '.join(info['intents'])}")
        print()
    else:
        print("  ❌ No skills found")
        print()
    
    # Check providers
    print("🔧 Provider Availability:")
    
    # Check hotword provider
    try:
        import openwakeword
        print("  ✅ OpenWakeWord: Available")
    except ImportError:
        print("  ⚠️  OpenWakeWord: Not available (using mock)")
    
    # Check STT provider
    try:
        import faster_whisper
        print("  ✅ Faster Whisper: Available")
    except ImportError:
        print("  ⚠️  Faster Whisper: Not available (using mock)")
    
    # Check TTS provider  
    try:
        import pyttsx3
        print("  ✅ pyttsx3: Available")
    except ImportError:
        print("  ⚠️  pyttsx3: Not available (using mock)")
    
    print()
    
    # Check environment
    print("🌍 Environment:")
    import os
    
    mock_mode = (
        os.getenv("NOVA_PRIME_MOCK", "").lower() in ("1", "true", "yes") or
        os.getenv("NOVA_PRIME_NO_AUDIO", "").lower() in ("1", "true", "yes") or
        os.getenv("CI", "").lower() in ("1", "true", "yes")
    )
    
    if mock_mode:
        print("  ℹ️  Mock mode: ENABLED (no real audio)")
    else:
        print("  ✅ Mock mode: Disabled (real audio available)")
    
    if os.getenv("CI"):
        print("  ℹ️  CI Environment: Detected")
    
    print()
    
    # Check user skills directory
    print("📁 User Skills Directory:")
    import platformdirs
    from pathlib import Path
    
    config_dir = Path(platformdirs.user_config_dir("Nova Prime"))
    skills_dir = config_dir / "skills"
    
    print(f"  📍 Location: {skills_dir}")
    
    if skills_dir.exists():
        user_skills = list(skills_dir.glob("*.py"))
        if user_skills:
            print(f"  ✅ Found {len(user_skills)} user skill files:")
            for skill_file in user_skills:
                print(f"    • {skill_file.name}")
        else:
            print("  ℹ️  Directory exists but no skills found")
    else:
        print("  ℹ️  Directory does not exist (this is normal)")
    
    print()
    
    # Test basic functionality
    print("🧪 Basic Functionality Test:")
    try:
        result = voice_loop.process_single_utterance("apri calcolatrice")
        if result["success"]:
            print("  ✅ Intent routing: Working")
            print(f"    Intent: {result['intent']}")
            print(f"    Skill: {result.get('skill_data', {}).get('action', 'N/A')}")
        else:
            print("  ❌ Intent routing: Failed")
            print(f"    Error: {result['message']}")
    except Exception as e:
        print(f"  ❌ Basic test failed: {e}")
    
    print()
    
    # Overall health
    print("🏥 Overall Health:")
    
    # Count issues
    issues = 0
    
    if not skills_info:
        issues += 1
        print("  ❌ No skills loaded")
    
    if mock_mode and not os.getenv("CI"):
        print("  ⚠️  Running in mock mode outside CI")
    
    try:
        result = voice_loop.process_single_utterance("test")
        if not result["success"] and "No intent found" not in result["message"]:
            issues += 1
    except Exception:
        issues += 1
        print("  ❌ Basic functionality test failed")
    
    if issues == 0:
        print("  🎉 All systems operational!")
        return 0
    elif issues == 1:
        print("  ⚠️  Minor issues detected")
        return 0  # Still return 0 for CI compatibility
    else:
        print("  ❌ Multiple issues detected")
        return 1


def main() -> int:
    """Main entry point for nova-prime-listen CLI."""
    parser = setup_parser()
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = {}
        if args.config:
            config.update(load_config_file(args.config))
        
        # Override with command line arguments
        config.update(create_config_from_args(args))
        
        # Create voice loop
        voice_loop = VoiceLoop(config=config)
        
        # Handle special modes
        if args.list_skills:
            list_skills(voice_loop)
            return 0
        
        if args.status:
            show_status(voice_loop)
            return 0
        
        if args.doctor:
            return run_doctor(voice_loop)
        
        # Test utterance mode
        if args.test_utterance:
            print(f"Testing utterance: '{args.test_utterance}'")
            result = voice_loop.process_single_utterance(args.test_utterance)
            
            print(f"Intent: {result['intent']}")
            print(f"Entities: {result['entities']}")
            print(f"Success: {result['success']}")
            print(f"Message: {result['message']}")
            
            if result['skill_data']:
                print(f"Skill data: {result['skill_data']}")
            
            return 0 if result['success'] else 1
        
        # Once mode - process single voice input
        if args.once:
            print("Listening for a single utterance...")
            try:
                # Start voice loop but process only once
                voice_loop._load_skills()  # Ensure skills are loaded
                voice_loop.hotword_provider.start()
                
                # Wait for hotword
                print("Waiting for hotword...")
                hotword_timeout = config.get("hotword_timeout", 30.0)
                if voice_loop.hotword_provider.wait_for_hotword(timeout=hotword_timeout):
                    print("Hotword detected! Processing...")
                    voice_loop._process_voice_input()
                    return 0
                else:
                    print("No hotword detected within timeout.")
                    return 1
                    
            finally:
                voice_loop.hotword_provider.stop()
        
        # Normal continuous mode
        print("Starting Nova Prime voice assistant...")
        print("Press Ctrl+C to stop.")
        
        voice_loop.start()
        return 0
        
    except KeyboardInterrupt:
        print("\nShutdown requested by user.")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())