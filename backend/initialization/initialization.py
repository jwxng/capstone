from backend.settings import settings

def initialization():
    user_settings = settings.settings
    if not user_settings.data["terms_agreed"]:
        # INCORPORATE FRONTEND IN THIS BLOCK
        print("Await user agreeing to terms.")
        user_settings.data["terms_agreed"] = True # must be True to proceed
        user_settings.save_data()

    print("Checking if app is fully set up...")
    user_settings.check_setup_complete()