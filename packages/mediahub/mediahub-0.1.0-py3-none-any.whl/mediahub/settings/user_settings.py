# src/settings/user_settings.py
import json

class UserSettings:
    def __init__(self, config_path):
        self.config_path = config_path
        self.settings = self.load_settings()

    def load_settings(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_settings(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def get_setting(self, key):
        return self.settings.get(key)

    def set_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()
