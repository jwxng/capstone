import pandas as pd

class DataTracker:
    def __init__(self):
        self.working_data = pd.DataFrame()
        self.session_start_time = None
        self.current_elapsed_time = 0
        self.last_alert_time = 0
    
    def update_current_elapsed_time(self, new_time):
        self.current_elapsed_time = new_time - self.session_start_time

    def update_last_alert_time(self, new_time):
        self.last_alert_time = new_time

    def reset_tracker(self):
        self.working_data = pd.DataFrame()
        self.session_start_time = None
        self.current_elapsed_time = 0
        self.last_alert_time = 0

data_tracker = DataTracker()