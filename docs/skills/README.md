# Nova Prime Skills System

Nova Prime uses an extensible skills system that allows you to add new voice-controlled functionality through Python modules. Skills are automatically discovered and loaded from both built-in and user-defined locations.

## Overview

A skill in Nova Prime is a Python class that:
- Inherits from the `Skill` base class
- Declares which intents it can handle
- Implements the logic to execute those intents
- Can extract entities from user input
- Returns structured results

## Quick Start

### Creating a Simple Skill

Create a file in your skills directory (e.g., `~/.config/Nova Prime/skills/hello.py`):

```python
from nova_prime.skills.base import Skill, SkillContext, SkillResult
from typing import Dict, List, Any

class HelloSkill(Skill):
    def __init__(self):
        super().__init__("hello")
    
    @property
    def intents(self) -> List[str]:
        return ["greet"]
    
    @property
    def description(self) -> str:
        return "Responds to greetings"
    
    def handle(self, intent: str, entities: Dict[str, Any], context: SkillContext) -> SkillResult:
        name = entities.get("name", "there")
        return SkillResult(
            success=True,
            message=f"Hello, {name}! How can I help you today?"
        )
```

### Adding Intent Mapping

To make your skill discoverable, you need to add intent mappings. You can either:

1. **Modify the intent router** (for system-wide changes)
2. **Use a skill manifest** (recommended for user skills)

Create a manifest file `~/.config/Nova Prime/skills/hello_manifest.yaml`:

```yaml
skill_name: "hello"
intent_mappings:
  "hello ": "greet"
  "hi ": "greet"
  "hey ": "greet"
```

## Skill Architecture

### Base Classes

#### `Skill` (Abstract Base Class)

All skills must inherit from this class:

```python
from nova_prime.skills.base import Skill, SkillContext, SkillResult

class MySkill(Skill):
    def __init__(self):
        super().__init__("my_skill_name")
    
    @property
    def intents(self) -> List[str]:
        """List of intent names this skill handles"""
        return ["my_intent"]
    
    @property
    def description(self) -> str:
        """Human-readable description of the skill"""
        return "Does something useful"
    
    def handle(self, intent: str, entities: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Main execution method"""
        # Your skill logic here
        return SkillResult(success=True, message="Done!")
```

#### `SkillContext`

Provides execution context to skills:

```python
class SkillContext:
    user_input: str      # Original user utterance
    is_mock: bool        # Whether running in mock/test mode
    config: Dict         # Configuration dictionary
    session_data: Dict   # Temporary session storage
```

#### `SkillResult`

Returned by skill execution:

```python
class SkillResult:
    success: bool        # Whether execution was successful
    message: str         # Response message to speak/display
    data: Dict          # Additional structured data
    should_speak: bool   # Whether TTS should speak the message
```

## Skill Discovery

Nova Prime automatically discovers skills from:

1. **Built-in skills**: `nova_prime.skills.builtin.*`
2. **User skills**: Platform-specific directories:
   - Linux: `~/.config/Nova Prime/skills/`
   - macOS: `~/Library/Application Support/Nova Prime/skills/`
   - Windows: `%APPDATA%/Nova Prime/skills/`

### Custom Skills Directory

You can specify a custom directory:

```bash
nova-prime-listen --user-skills-dir /path/to/my/skills
```

## Entity Extraction

Skills can extract structured data from user input through the intent router:

### Common Entity Types

```python
# App names
entities = {"app_name": "calculator", "original_name": "calcolatrice"}

# Numbers and percentages
entities = {"volume_percent": 75, "action": "set"}

# Actions
entities = {"action": "increase"}  # increase, decrease, set, get
```

### Custom Entity Extraction

Override the intent router for custom entity extraction:

```python
from nova_prime.core.intent_router import IntentRouter

class CustomIntentRouter(IntentRouter):
    def _extract_entities(self, intent_name: str, text: str) -> Dict[str, Any]:
        entities = super()._extract_entities(intent_name, text)
        
        if intent_name == "my_custom_intent":
            # Custom extraction logic
            entities["custom_field"] = self._extract_custom_field(text)
        
        return entities
```

## Built-in Skills

Nova Prime includes several built-in skills:

### `open_app` - Application Launcher

**Intents**: `open_app`

**Entities**:
- `app_name`: Normalized application name
- `original_name`: Original name from user input

**Example commands**:
- "open calculator" / "apri calcolatrice"
- "launch notepad" / "lancia blocco note"

**Mock behavior**: Returns execution plan without launching apps

### `system_volume` - Volume Control

**Intents**: `system_volume`

**Entities**:
- `action`: get, set, increase, decrease
- `volume_percent`: Target or change percentage

**Example commands**:
- "set volume to 50%" / "imposta volume a 50%"
- "volume up" / "alza volume"

**Mock behavior**: Simulates volume changes with fake values

## Advanced Topics

### State Management

Skills can maintain state using the context object:

```python
def handle(self, intent: str, entities: Dict[str, Any], context: SkillContext) -> SkillResult:
    # Access session data
    count = context.session_data.get("count", 0)
    count += 1
    context.session_data["count"] = count
    
    return SkillResult(success=True, message=f"Count is now {count}")
```

### Configuration

Skills can access configuration through context:

```python
def handle(self, intent: str, entities: Dict[str, Any], context: SkillContext) -> SkillResult:
    api_key = context.config.get("my_skill_api_key")
    if not api_key:
        return SkillResult(success=False, message="API key not configured")
    
    # Use API key...
```

### Mock vs Real Mode

Skills should behave differently in mock mode for CI/testing:

```python
def handle(self, intent: str, entities: Dict[str, Any], context: SkillContext) -> SkillResult:
    if context.is_mock:
        # Return mock result for testing
        return SkillResult(success=True, message="Mock action completed")
    else:
        # Perform real action
        return self._perform_real_action(entities)
```

### Error Handling

Robust error handling is important:

```python
def handle(self, intent: str, entities: Dict[str, Any], context: SkillContext) -> SkillResult:
    try:
        result = self._risky_operation(entities)
        return SkillResult(success=True, message=f"Completed: {result}")
    except ValueError as e:
        return SkillResult(success=False, message=f"Invalid input: {e}")
    except Exception as e:
        return SkillResult(success=False, message=f"Unexpected error: {e}")
```

### Validation

Validate entities before processing:

```python
def validate_entities(self, intent: str, entities: Dict[str, Any]) -> bool:
    if intent == "my_intent":
        return "required_field" in entities
    return True
```

## Testing Skills

### Unit Testing

Test skills in isolation:

```python
import pytest
from nova_prime.skills.base import SkillContext
from my_skills.hello import HelloSkill

def test_hello_skill():
    skill = HelloSkill()
    context = SkillContext(user_input="hello world", is_mock=True)
    
    result = skill.handle("greet", {"name": "Alice"}, context)
    
    assert result.success is True
    assert "Alice" in result.message
```

### Integration Testing

Test with the full voice loop:

```python
from nova_prime.core.voice_loop import VoiceLoop

def test_skill_integration():
    voice_loop = VoiceLoop(config={"mock": True})
    result = voice_loop.process_single_utterance("hello Alice")
    
    assert result["success"] is True
    assert "Alice" in result["message"]
```

## Best Practices

### 1. Clear Intent Names

Use descriptive, unique intent names:
```python
# Good
intents = ["send_email", "check_email", "delete_email"]

# Avoid
intents = ["email"]  # Too generic
```

### 2. Graceful Degradation

Handle missing dependencies gracefully:

```python
def __init__(self):
    super().__init__("weather")
    try:
        import requests
        self.has_requests = True
    except ImportError:
        self.has_requests = False

def handle(self, intent: str, entities: Dict[str, Any], context: SkillContext) -> SkillResult:
    if not self.has_requests:
        return SkillResult(
            success=False, 
            message="Weather skill requires 'requests' library"
        )
    # ... rest of implementation
```

### 3. Internationalization

Support multiple languages:

```python
def handle(self, intent: str, entities: Dict[str, Any], context: SkillContext) -> SkillResult:
    lang = context.config.get("language", "en")
    
    messages = {
        "en": "Task completed successfully",
        "it": "Attività completata con successo",
        "es": "Tarea completada exitosamente"
    }
    
    message = messages.get(lang, messages["en"])
    return SkillResult(success=True, message=message)
```

### 4. Platform Compatibility

Handle platform differences:

```python
import platform

def handle(self, intent: str, entities: Dict[str, Any], context: SkillContext) -> SkillResult:
    system = platform.system().lower()
    
    if system == "windows":
        return self._handle_windows(entities)
    elif system == "darwin":
        return self._handle_macos(entities)
    elif system == "linux":
        return self._handle_linux(entities)
    else:
        return SkillResult(
            success=False,
            message=f"Unsupported platform: {system}"
        )
```

## Debugging Skills

### Logging

Use logging for debugging:

```python
import logging

class MySkill(Skill):
    def __init__(self):
        super().__init__("my_skill")
        self.logger = logging.getLogger(f"nova_prime.skills.{self.name}")
    
    def handle(self, intent: str, entities: Dict[str, Any], context: SkillContext) -> SkillResult:
        self.logger.debug(f"Handling intent {intent} with entities {entities}")
        # ... skill logic
```

### Verbose Mode

Test with verbose logging:

```bash
nova-prime-listen --verbose --test-utterance "my command"
```

## Contributing Skills

To contribute skills to Nova Prime:

1. Create skills in `nova_prime/skills/builtin/`
2. Add comprehensive tests
3. Update documentation
4. Ensure cross-platform compatibility
5. Support both mock and real modes

## Reference

### File Structure
```
~/.config/Nova Prime/skills/
├── my_skill.py              # Skill implementation
├── my_skill_manifest.yaml   # Intent mappings (optional)
└── __init__.py             # Package marker (optional)
```

### Environment Variables
- `NOVA_PRIME_MOCK=1`: Force mock mode for all skills
- `NOVA_PRIME_NO_AUDIO=1`: Disable audio-related functionality

### CLI Commands
```bash
nova-prime-listen --list-skills        # Show all loaded skills
nova-prime-listen --status            # Show system status
nova-prime-listen --test-utterance    # Test specific commands
```