#!/usr/bin/env python3
"""配置管理"""
import json
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".pw-repl"
CONFIG_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = CONFIG_DIR / "history"
ALIASES_FILE = CONFIG_DIR / "aliases"

DEFAULTS = {
    "cdp_url": "127.0.0.1:9222",
    "smgr_url": "https://session-manager-api.fly.dev",
    "smgr_key": "a12345",
    "screenshot_dir": ".",
    "timeout": 30,
    "history_size": 1000,
}

class Config:
    def __init__(self):
        self._data = DEFAULTS.copy()
        self._load()
    
    def _load(self):
        if CONFIG_FILE.exists():
            try:
                saved = json.loads(CONFIG_FILE.read_text())
                # 只覆盖非空值
                for k, v in saved.items():
                    if v:  # 跳过空值
                        self._data[k] = v
            except: pass
    
    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(self._data, indent=2))
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any):
        self._data[key] = value
        self.save()
    
    def all(self) -> dict:
        return self._data.copy()

config = Config()
