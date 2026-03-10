import backend.constants
import eel
import pandas as pd

from backend.data.data_analysis import data_analysis
from backend.data.data_calibration import data_calibration
from backend.data.data_tracker import data_tracker

@eel.expose
def data_retrieval(rows, columns):    
    if not rows or not columns:
        print("No data received.")
        return

    if not isinstance(rows[0], list):
        rows = [rows]
        
    working_df = pd.DataFrame(rows, columns=columns)
    # create column for timestamps measured in seconds
    working_df['timestamp_s'] = working_df['timestamp_ms'].astype(float) / 1000.0
        
    if data_tracker.working_data.empty:
        data_tracker.session_start_time = working_df['timestamp_s'].iloc[0]
        data_tracker.working_data = working_df
    else:
        data_tracker.working_data = pd.concat([data_tracker.working_data, working_df], ignore_index=True)
        # Remove older entries
        data_tracker.working_data = data_tracker.working_data.tail(backend.constants.WORKING_DATA_LENGTH)

    data_tracker.update_current_elapsed_time(data_tracker.working_data['timestamp_s'].iloc[-1])
    
    print("Successfully received data.")
    print(data_tracker.working_data)
    # attempt to save calibration data (only occurs once per session, and when there is no existing data)
    data_calibration.save_data(data_tracker.working_data)
    # perform analyses
    data_analysis(data_tracker.working_data)


@eel.expose
def data_clear():
    data_tracker.reset_tracker()
    print("Memory cleared.")
    print(data_tracker.working_data)