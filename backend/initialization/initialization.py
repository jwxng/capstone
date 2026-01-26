import eel
from backend.settings import settings

user_settings = settings.settings

def initialization():
    if not user_settings.data["terms_agreed"]:
        print("Await user agreeing to terms.")
        eel.start("welcome.html")
    else:
        eel.start("index.html")
    

@eel.expose
def terms_agreed():
    print("Terms agreed.")
    user_settings.data["terms_agreed"] = True 
    user_settings.save_data()