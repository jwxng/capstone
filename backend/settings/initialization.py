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