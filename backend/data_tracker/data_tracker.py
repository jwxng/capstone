class DataTracker:
    def __init__(self):
        self.data = {
            "last_warning": 0,
        }

    def update_tracker(self, new_time):
        self.data["last_warning"] = new_time

    def reset_tracker(self):
        self.data["last_warning"] = 0

data_tracker = DataTracker()