import json
import os

class Settings:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.default_settings = {
            "cache_dir": "C:\\RS-AI-Cache",
            "cache_size_gb": 50,
            "ollama_model": "llama3",
            "voice_enabled": True,
            "language": "English"
        }
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = self.default_settings
            self.save()

    def save(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key):
        return self.settings.get(key, self.default_settings.get(key))

    def set(self, key, value):
        self.settings[key] = value
        self.save()
