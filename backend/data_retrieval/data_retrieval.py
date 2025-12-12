import eel
import pandas as pd

@eel.expose
def data_retrieval(rows, columns):
    if not rows or not columns:
        print("No data received.")

    rows = [rows]
    # Convert to DataFrame
    df = pd.DataFrame(rows, columns=columns)
    
    print("Successfully received data.")
    print(df.head())