import numpy as np
import pandas as pd

SQUINT_THRESHOLD = 0.3
JAW_OPEN_THRESHOLD = 0.6
MIN_YAWN_SECONDS = 1.0
MAX_YAWN_SECONDS = 6.0

def data_analysis(df):
    # called by data_logging.py
    print("Analyzing data.")
    detect_squints(df.tail(1))
    # detect_yawns(df)

def detect_squints(df):
    avg_squint = (df['eyeSquintLeft'] + df['eyeSquintRight']) / 2
    is_squinting = (avg_squint > SQUINT_THRESHOLD).astype(int)

    if (is_squinting == 1).any():
        print("ALERT: Squinting Detected!")

def detect_yawns(df):
    # We need the time_s conversion from your notebook to check duration
    # We'll use the relative time within this batch
    times = df['timestamp_ms'] / 1000.0
    
    is_jaw_open = df['jawOpen'] > JAW_OPEN_THRESHOLD
    transitions = np.diff(is_jaw_open.astype(int))
    
    starts = np.where(transitions == 1)[0] + 1
    ends = np.where(transitions == -1)[0] + 1
    
    # Loop through pairs of start/end to check duration
    for s_idx, e_idx in zip(starts, ends):
        duration = times.iloc[e_idx] - times.iloc[s_idx]
        if MIN_YAWN_SECONDS <= duration <= MAX_YAWN_SECONDS:
            print(f"--- ALERT: Yawn detected! Duration: {round(duration, 2)}s ---")