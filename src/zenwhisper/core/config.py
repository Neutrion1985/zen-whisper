import json
import os
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "zenwhisper"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.defaults = {
            "language": "en",
            "model_size": "base",
            "microphone_id": None,
            "sound_enabled": True,
            "autostart": False,
            "mic_gain": 1.0,
            "hotkey": "<ctrl>+<f12>",
            "vocabulary": [],
            "snippets": {}
        }
        self.settings = self.load()

    def load(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**self.defaults, **data}
            except Exception as e:
                print(f"DEBUG: Error loading config: {e}")
        return self.defaults.copy()

    def save(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"DEBUG: Error saving config: {e}")

    def get(self, key):
        return self.settings.get(key, self.defaults.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save()

# Global instance
config = ConfigManager()
