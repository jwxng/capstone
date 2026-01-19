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
    detect_yawns(df)

def detect_squints(df):
    avg_squint = (df['eyeSquintLeft'] + df['eyeSquintRight']) / 2
    is_squinting = (avg_squint > SQUINT_THRESHOLD).astype(int)

    if (is_squinting == 1).any():
        print("ALERT: Squinting Detected!")

def detect_yawns(df):
    times = df['timestamp_ms'].astype(float) / 1000.0
    
    jaw_open_transition = np.diff((df['jawOpen'] > JAW_OPEN_THRESHOLD).astype(int))
    starts = np.where(jaw_open_transition == 1)[0] + 1
    ends = np.where(jaw_open_transition == -1)[0] + 1

    # Loop through pairs of start/end times to check yawn duration
    for start, end in zip(starts, ends):
        duration = times.iloc[end] - times.iloc[start]
        if MIN_YAWN_SECONDS <= duration <= MAX_YAWN_SECONDS:
            print(f"ALERT: Yawn Detected! Duration: {round(duration, 2)}s ---")