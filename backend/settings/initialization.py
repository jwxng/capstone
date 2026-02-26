import eel
from backend.settings.settings import settings as user_settings

def initialization():
    if not user_settings.data["terms_agreed"]:
        print("Await user agreeing to terms.")
        eel.start("pages/welcome/welcome.html", mode=None, block=False)
    else:
        eel.start("index.html", mode=None, block=False)

@eel.expose
def terms_agreed():
    print("Terms agreed.")
    user_settings.data["terms_agreed"] = True 
    user_settings.save_data()

@eel.expose
def go_home():
    eel.start("index.html", mode=None, block=False)