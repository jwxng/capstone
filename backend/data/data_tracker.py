import backend.constants
import eel
import pandas as pd

class DataTracker:
    def __init__(self):
        self.working_data = pd.DataFrame()
        self.session_start_time = None
        self.current_elapsed_time = 0
        self.last_alert_time = 0
        self.screen_time_threshold = backend.constants.SCREEN_TIME_THRESHOLD_SECONDS

        self.exercise_opened = False
        self.active_exercise = None 
        self.exercise_start_time = 0
    
    def update_current_elapsed_time(self, new_time):
        self.current_elapsed_time = new_time - self.session_start_time

    def try_triggering_alert(self, frontend_game):
        if not self.exercise_opened and self.current_elapsed_time - self.last_alert_time > backend.constants.SECONDS_BETWEEN_WARNINGS:
            print("At least " + str(backend.constants.SECONDS_BETWEEN_WARNINGS) + " have passed; alert user.")
            eel.trigger_game(frontend_game)()

    def check_screen_time(self):
        if self.current_elapsed_time >= self.screen_time_threshold:
            self.screen_time_threshold += backend.constants.SCREEN_TIME_THRESHOLD_SECONDS
            print("Screen time threshold has been exceeded.")
            self.try_triggering_alert('20-20-20/20-20-20.html')

    def reset_tracker(self):
        self.working_data = pd.DataFrame()
        self.session_start_time = None
        self.current_elapsed_time = 0
        self.last_alert_time = 0
        self.screen_time_threshold = backend.constants.SCREEN_TIME_THRESHOLD_SECONDS

        self.active_exercise = None
        self.exercise_start_time = 0

data_tracker = DataTracker()

@eel.expose
def open_exercise():
    data_tracker.exercise_opened = True

@eel.expose
def close_exercise():
    data_tracker.exercise_opened = False
    data_tracker.last_alert_time = data_tracker.current_elapsed_time