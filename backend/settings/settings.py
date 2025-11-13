import json
import os

CONFIG_FILE = 'settings.json'

class Settings:
    def __init__(self):
        print("Initializing config settings, loading default values.")
        self.data = {
            "app_initialized": False,
            "terms_agreed": False,
            "webcam_calibrated": False,
            "sound_enabled": False,
            "alerts_enabled": False,
            "notifs_enabled": False,
        }
        self.load_data()

    def load_data(self):
        print("Checking for existing config settings...")
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    existing_data = json.load(f)
                    self.data.update(existing_data)
                    print("Existing config settings loaded.")
            except Exception as e:
                print(f"Error loading config settings: {e}")
        else:
            print("No config settings file found.")

    def save_data(self):
        print("Saving settings config...")
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.data, f, indent=4)
                print("Configuration saved.")
        except Exception as e:
            print(f"Error saving config: {e}")

    def check_setup_complete(self):
        if self.data["terms_agreed"] and self.data["webcam_calibrated"]:
            print("App is fully set up.")
            self.data["app_initialized"] = True
            self.save_data()

settings = Settings()