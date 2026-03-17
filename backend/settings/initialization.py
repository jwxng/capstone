import eel
from backend.settings.settings import settings as user_settings

def initialization():
    eel.start("index.html", mode=None, block=False)

@eel.expose
def terms_agreed():
    print("Terms agreed.")
    user_settings.data["terms_agreed"] = True 
    user_settings.save_data()

@eel.expose
def go_home():
    eel.start("index.html", mode=None, block=False)

@eel.expose
def get_settings():
    return {
        "blink_rate": user_settings.data.get("blink_rate", True),
        "perclos": user_settings.data.get("perclos", True),
        "head_tilt": user_settings.data.get("head_tilt", True),
        "screen_time": user_settings.data.get("screen_time", True),
    }

@eel.expose
def save_settings(data):
    user_settings.data["blink_rate"] = data.get("blink_rate", True)
    user_settings.data["perclos"] = data.get("perclos", True)
    user_settings.data["head_tilt"] = data.get("head_tilt", True)
    user_settings.data["screen_time"] = data.get("screen_time", True)
    user_settings.save_data()

@eel.expose
def get_points():
    return user_settings.data["points"]

@eel.expose
def add_points(amount):
    user_settings.data["points"] += amount
    user_settings.save_data()
    return user_settings.data["points"]