import json
import os
import pandas as pd

CONFIG_FILE = 'calibration_data.csv'
REQUIRED_CALIBRATION_SECONDS = 300

class DataCalibration:
    def __init__(self):
        self.data = pd.DataFrame()
        self.baseline_blink_rate = None
        self.load_data()
        

    def load_data(self):
        print("Checking for existing calibration data...")
        if os.path.exists(CONFIG_FILE):
            try:
                existing_data = pd.read_csv(CONFIG_FILE)
                calibration_duration = existing_data['timestamp_s'].iloc[-1] - existing_data['timestamp_s'].iloc[0]

                if calibration_duration >= REQUIRED_CALIBRATION_SECONDS:
                    self.data = existing_data
                    #find the baseline blink rate
                    self.baseline_blink_rate = blink_calibration(existing_data)
                    print("Existing calibration data loaded.")
                    print(f"Blink rate: {self.baseline_blink_rate}")
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
                #store baseline
                self.baseline_blink_rate = blink_calibration(df)
                df.to_csv(CONFIG_FILE)
                print("Calibration data saved.")
            except Exception as e:
                print(f"Error saving calibration data: {e}")

    def get_baseline(self):
        #return calibrated blink rate
        return self.baseline_blink_rate



#Calibration 
"""
The calibration function is only going to be done for the blink rate, where we will collect user data for about 5 minutes to establish what
the users 'ideal' blink rate. The calibration value will then be compared against by the blink-rate being measured in real-time. If the real-time
measurements detect that the users blink rate has fallen significantly below the established baseline, then the appropriate game will be called
"""

def blink_calibration(df):

    BLINK_START_THRESHOLD = 0.6
    BLINK_END_THRESHOLD = 0.3

    #calibration will take 5 minutes (300s)
    df_start_time = df['timestamp_s'].iloc[0]
    df_duration = 300
    calibration_end_time = df_start_time + df_duration
   

    avg_blink = (df['eyeBlinkLeft'] + df['eyeBlinkRight']) / 2

    blink_count = 0
    total_blinking_time = 0

    is_blinking = False
    blink_start_time = None
    blink_end_time = None
    prev_blink_val = avg_blink[0]

    for i in range(len(avg_blink)):
        curr_time = df['timestamp_s'].iloc[i]

        #this is to ensure that only the first 5 minutes of data are used to calibrate the user's blink rate
        if curr_time > calibration_end_time:
            break

        curr_blink_val = avg_blink.iloc[i]

        if not is_blinking and prev_blink_val <= BLINK_START_THRESHOLD and curr_blink_val > BLINK_START_THRESHOLD:
            is_blinking = True
            blink_start_time = curr_time
       
        elif is_blinking and prev_blink_val >= BLINK_END_THRESHOLD and curr_blink_val < BLINK_END_THRESHOLD:
            is_blinking = False
            blink_end_time = curr_time
            curr_duration = blink_end_time - blink_start_time
            total_blinking_time += curr_duration
            blink_count += 1

        prev_blink_val = curr_blink_val

    return (blink_count / (df_duration / 60))
    

data_calibration = DataCalibration()