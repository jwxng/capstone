import eel
import pandas as pd

from backend.alert_tracker import alert_tracker
from backend.data_analysis import data_analysis
from backend.data_calibration import data_calibration

working_data = pd.DataFrame()
calibration_data = data_calibration.data_calibration

@eel.expose
def data_retrieval(rows, columns):
    global working_data
    
    if not rows or not columns:
        print("No data received.")
        return

    rows = [rows]
    working_df = pd.DataFrame(rows, columns=columns)
        
    if working_data.empty:
        working_data = working_df
    else:
        working_data = pd.concat([working_data, working_df], ignore_index=True)
        # Remove older entries
        working_data = working_data.tail(72000)
    
    print("Successfully received data.")

    # create column for timestamps measured in seconds
    working_data['timestamp_s'] = working_data['timestamp_ms'].astype(float) / 1000.0

    # attempt to save calibration data (only occurs once per session, and when there is no existing data)
    calibration_data.save_data(working_data)

    data_analysis.data_analysis(working_data)


@eel.expose
def data_clear():
    global working_data
    alert_tracker_data = alert_tracker.alert_tracker

    working_data = pd.DataFrame()
    alert_tracker_data.reset_tracker()
    print("Memory cleared.")
    print(working_data)