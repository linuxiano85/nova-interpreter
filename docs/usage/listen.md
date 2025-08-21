# Nova Prime Voice Assistant - Listen Command

The `nova-prime-listen` command provides a voice-controlled interface for Nova Prime, allowing you to interact with your system using spoken commands.

## Quick Start

### Basic Usage

```bash
# Start the voice assistant (requires microphone and speakers)
nova-prime-listen

# Start in mock mode (no audio hardware required)
nova-prime-listen --mock

# Process a single command and exit
nova-prime-listen --once

# Test a specific phrase without voice input
nova-prime-listen --test-utterance "open calculator"
```

### Installation and Setup

1. Install Nova Prime with voice dependencies:
```bash
pip install -e .
```

2. For real audio functionality (optional), install audio dependencies:
```bash
# For hotword detection
pip install openwakeword

# For speech-to-text
pip install faster-whisper

# For text-to-speech
pip install pyttsx3
```

## Command Options

### Operation Modes

| Option | Description |
|--------|-------------|
| `--mock` | Force mock providers (no real audio I/O) |
| `--no-audio` | Disable audio I/O |
| `--once` | Process a single utterance and exit |

### Configuration

| Option | Description |
|--------|-------------|
| `--config <path>` | Path to configuration file (JSON or YAML) |
| `--user-skills-dir <path>` | Custom user skills directory |

### Timeouts and Thresholds

| Option | Default | Description |
|--------|---------|-------------|
| `--hotword-timeout <seconds>` | 30.0 | Hotword detection timeout |
| `--stt-timeout <seconds>` | 5.0 | Speech-to-text timeout |

### Logging

| Option | Description |
|--------|-------------|
| `--verbose`, `-v` | Enable verbose logging |
| `--quiet`, `-q` | Enable quiet mode (warnings and errors only) |

### Information and Testing

| Option | Description |
|--------|-------------|
| `--list-skills` | List available skills and exit |
| `--status` | Show status information and exit |
| `--test-utterance <text>` | Test a specific utterance without voice input |

## Usage Examples

### Local Development

```bash
# Start with verbose logging for debugging
nova-prime-listen --verbose

# Test without audio hardware
nova-prime-listen --mock --verbose

# Test a specific command
nova-prime-listen --test-utterance "set volume to 75%"
```

### CI/Testing

```bash
# Run in CI environment (automatically uses mocks)
NOVA_PRIME_MOCK=1 nova-prime-listen --once --test-utterance "apri calcolatrice"

# Force mock mode and process once
nova-prime-listen --mock --once

# Test all skills
nova-prime-listen --list-skills
```

### Production Use

```bash
# Start with custom configuration
nova-prime-listen --config /path/to/config.yaml

# Start with custom user skills directory
nova-prime-listen --user-skills-dir /path/to/my/skills
```

## Environment Variables

Nova Prime respects several environment variables:

| Variable | Effect |
|----------|--------|
| `NOVA_PRIME_MOCK=1` | Force mock mode |
| `NOVA_PRIME_NO_AUDIO=1` | Disable audio I/O |
| `CI=1` | Automatically enable mock mode |

## Configuration File

You can use a configuration file (JSON or YAML) to set default options:

### config.yaml
```yaml
# Audio settings
mock: false
no_audio: false

# Timeouts (seconds)
hotword_timeout: 30.0
stt_timeout: 5.0

# Directories
user_skills_dir: "/path/to/my/skills"

# Logging
log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR
```

### config.json
```json
{
  "mock": false,
  "no_audio": false,
  "hotword_timeout": 30.0,
  "stt_timeout": 5.0,
  "user_skills_dir": "/path/to/my/skills",
  "log_level": "INFO"
}
```

## Supported Voice Commands

Nova Prime comes with built-in skills for common tasks:

### Application Launching
- "open calculator" / "apri calcolatrice"
- "open notepad" / "apri blocco note"
- "open browser" / "apri browser"
- "open chrome" / "apri chrome"

### Volume Control
- "set volume to 50%" / "imposta volume a 50%"
- "volume up" / "alza volume"
- "volume down" / "abbassa volume"
- "what's the volume?" / "qual è il volume?"

## Troubleshooting

### Audio Issues

If you experience audio problems:

1. Test with mock mode first:
```bash
nova-prime-listen --mock --test-utterance "open calculator"
```

2. Check audio dependencies:
```bash
pip install openwakeword faster-whisper pyttsx3
```

3. Try without audio:
```bash
nova-prime-listen --no-audio --test-utterance "open calculator"
```

### Skills Not Loading

1. List available skills:
```bash
nova-prime-listen --list-skills
```

2. Check verbose output:
```bash
nova-prime-listen --verbose --status
```

3. Verify skills directory exists:
```bash
# Default user skills directory varies by platform:
# Linux: ~/.config/Nova Prime/skills/
# macOS: ~/Library/Application Support/Nova Prime/skills/
# Windows: %APPDATA%/Nova Prime/skills/
```

### Permission Issues

On some systems, you may need additional permissions for audio access or application launching. Run with `--mock` for testing without system permissions.

## Integration with CI

Nova Prime is designed to work in CI environments without hardware dependencies:

```yaml
# GitHub Actions example
- name: Test Nova Prime Voice Loop
  run: |
    nova-prime-listen --mock --once --test-utterance "apri calcolatrice"
  env:
    NOVA_PRIME_MOCK: "1"
```

The command automatically detects CI environments and switches to mock mode for reliable testing.

## Next Steps

- [Writing Custom Skills](../skills/README.md)
- [Voice Loop Architecture](../architecture/voice-loop.md)
- [Provider System](../architecture/providers.md)