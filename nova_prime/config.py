import json
import os
from dataclasses import dataclass, asdict
from typing import Optional

from platformdirs import user_config_dir

APP_NAME = "nova-prime"

@dataclass
class NovaConfig:
    language: str = "it"
    wake_word: str = "hey nova"
    global_hotkey: str = "ctrl+alt+n"
    listen_on_start: bool = True
    stt_backend: str = "faster-whisper"  # "faster-whisper" | "openai" | "whisper"
    tts_backend: Optional[str] = None
    use_os_mode: bool = True
    model_provider: str = "openai"  # "openai" | "anthropic" | "local"
    model_name: str = "gpt-4o"
    local_model_path: Optional[str] = None
    show_waveform_on_listen: bool = True

class ConfigStore:
    def __init__(self):
        self.dir = user_config_dir(APP_NAME)
        os.makedirs(self.dir, exist_ok=True)
        self.path = os.path.join(self.dir, "config.json")

    def load(self) -> NovaConfig:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return NovaConfig(**data)
            except Exception:
                pass
        cfg = NovaConfig()
        self.save(cfg)
        return cfg

    def save(self, cfg: NovaConfig):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(asdict(cfg), f, ensure_ascii=False, indent=2)