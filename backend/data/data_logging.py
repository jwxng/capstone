import eel
import pandas as pd

from backend.data.alert_tracker import alert_tracker
from backend.data.data_analysis import data_analysis
from backend.data.data_calibration import data_calibration

WORKING_DATA_LENGTH = 6000
working_data = pd.DataFrame()

@eel.expose
def data_retrieval(rows, columns):
    global working_data
    
    if not rows or not columns:
        print("No data received.")
        return

    if not isinstance(rows[0], list):
        rows = [rows]
        
    working_df = pd.DataFrame(rows, columns=columns)
    # create column for timestamps measured in seconds
    working_df['timestamp_s'] = working_df['timestamp_ms'].astype(float) / 1000.0
        
    if working_data.empty:
        alert_tracker.session_start_time = working_df['timestamp_s'].iloc[0]
        working_data = working_df
    else:
        working_data = pd.concat([working_data, working_df], ignore_index=True)
        # Remove older entries
        working_data = working_data.tail(WORKING_DATA_LENGTH)

    alert_tracker.update_current_elapsed_time(working_data['timestamp_s'].iloc[-1])
    
    print("Successfully received data.")

    # attempt to save calibration data (only occurs once per session, and when there is no existing data)
    data_calibration.save_data(working_data)

    data_analysis(working_data)


@eel.expose
def data_clear():
    global working_data

    working_data = pd.DataFrame()
    alert_tracker.reset_tracker()
    print("Memory cleared.")
    print(working_data)