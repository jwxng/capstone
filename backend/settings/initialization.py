import eel
from backend.settings.settings import settings as user_settings
import threading
import time

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

def start_screen_time_timer():
    def timer_loop():
        while True:
            time.sleep(1200)  # 20 minutes
            print("20 minutes passed; triggering 20-20-20")
            eel.trigger_game('20-20-20/20-20-20.html')
    
    thread = threading.Thread(target=timer_loop, daemon=True)
    thread.start()