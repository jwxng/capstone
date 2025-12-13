import eel
import pandas as pd

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
    
    print("Successfully received data.")
    print(working_data)


@eel.expose
def data_clear():
    global working_data

    working_data = pd.DataFrame()
    print("Memory cleared.")
    print(working_data)