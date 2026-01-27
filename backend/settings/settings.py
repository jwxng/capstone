import json
import os

CONFIG_FILE = 'settings.json'

class Settings:
    def __init__(self):
        self.data = {
            "terms_agreed": False,
        }
        self.load_data()

    def load_data(self):
        print("Checking for existing settings...")
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    existing_data = json.load(f)
                    self.data.update(existing_data)
                    print("Existing settings loaded.")
            except Exception as e:
                print(f"Error loading settings: {e}")
        else:
            print("No settings file found.")

    def save_data(self):
        print("Saving settings...")
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.data, f, indent=4)
                print("Settings saved.")
        except Exception as e:
            print(f"Error saving settings: {e}")

settings = Settings()