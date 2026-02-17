import eel
import pandas as pd

from backend.data_analysis import data_analysis
from backend.data_tracker import data_tracker

working_data = pd.DataFrame()

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
    data_analysis.data_analysis(working_data)


@eel.expose
def data_clear():
    global working_data
    current_tracked_data = data_tracker.data_tracker

    working_data = pd.DataFrame()
    current_tracked_data.reset_tracker()
    print("Memory cleared.")
    print(working_data)