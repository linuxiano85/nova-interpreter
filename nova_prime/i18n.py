import json
import os
from typing import Dict

def load_translations(lang: str) -> Dict[str, str]:
    base_dir = os.path.join(os.path.dirname(__file__), "i18n")
    path = os.path.join(base_dir, f"{lang}.json")
    if not os.path.exists(path):
        path = os.path.join(base_dir, "en.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def t(key: str, tr: Dict[str, str]) -> str:
    return tr.get(key, key)