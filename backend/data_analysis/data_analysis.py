import numpy as np
import pandas as pd

SQUINT_THRESHOLD = 0.3
JAW_OPEN_THRESHOLD = 0.6
MIN_YAWN_SECONDS = 1.0
MAX_YAWN_SECONDS = 6.0
BLINK_START_THRESHOLD = 0.4
BLINK_END_THRESHOLD = 0.2

def data_analysis(df):
    # called by data_logging.py
    print("Analyzing data.")
    detect_squints(df.tail(1))
    detect_yawns(df)
    detect_blinks(df)

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

    # loop through pairs of start/end times to check yawn duration
    for start, end in zip(starts, ends):
        duration = times.iloc[end] - times.iloc[start]
        if MIN_YAWN_SECONDS <= duration <= MAX_YAWN_SECONDS:
            print(f"ALERT: Yawn lasting {round(duration, 2)}s was Detected!")

def detect_blinks(df):
    times = df['timestamp_ms'].astype(float) / 1000.0
    avg_blink = (df['eyeBlinkLeft'] + df['eyeBlinkRight']) / 2
    total_duration = times.iloc[-1] - times.iloc[0]

    is_blinking = False
    blink_count = 0
    total_blinking_time = 0

    blink_start_time = None
    blink_end_time = None
    prev_blink_val = avg_blink[0]

    for i in range(len(avg_blink)):
        curr_time = times.iloc[i]
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

    blink_rate = blink_count / (total_duration / 60)
    print(f"Current Blink Rate: {round(blink_rate, 2)} blinks/min")