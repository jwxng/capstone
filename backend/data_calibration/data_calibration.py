import json
import os
import pandas as pd

CONFIG_FILE = 'calibration_data.csv'
REQUIRED_CALIBRATION_SECONDS = 300

class DataCalibration:
    def __init__(self):
        self.data = pd.DataFrame()
        self.load_data()

    def load_data(self):
        print("Checking for existing calibration data...")
        if os.path.exists(CONFIG_FILE):
            try:
                existing_data = pd.read_csv(CONFIG_FILE)
                calibration_duration = existing_data['timestamp_s'].iloc[-1] - existing_data['timestamp_s'].iloc[0]

                if calibration_duration >= REQUIRED_CALIBRATION_SECONDS:
                    self.data = existing_data
                    print("Existing calibration data loaded.")
                else:
                    print("Not enough existing calibration data; restarting calibration process.")

            except Exception as e:
                print(f"Error loading calibration data: {e}")
        else:
            print("No calibration data found.")

    def save_data(self, df: pd.DataFrame):
        current_duration = df['timestamp_s'].iloc[-1] - df['timestamp_s'].iloc[0]
        if current_duration >= REQUIRED_CALIBRATION_SECONDS and self.data.empty:
            print("Saving calibration data...")
            try:
                self.data = df
                df.to_csv(CONFIG_FILE)
                print("Calibration data saved.")
            except Exception as e:
                print(f"Error saving calibration data: {e}")

data_calibration = DataCalibration()